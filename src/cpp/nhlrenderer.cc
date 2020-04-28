// -*- mode: c++; c-basic-offset: 2; indent-tabs-mode: nil; -*-
#include "led-matrix.h"
#include "graphics.h"

#include <string>

#include <getopt.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#include "rapidjson/document.h"
#include "rapidjson/filereadstream.h"
#include <cstdio>

using namespace rapidjson;
using namespace rgb_matrix;

volatile bool interrupt_received = false;
static void InterruptHandler(int signo) {
  interrupt_received = true;
}

static int usage(const char *progname) {
  fprintf(stderr, "usage: %s [options] <text>\n", progname);
  fprintf(stderr, "Options:\n");
  rgb_matrix::PrintMatrixFlags(stderr);
  return 1;
}

static bool FullSaturation(const Color &c) {
  return (c.r == 0 || c.r == 255)
    && (c.g == 0 || c.g == 255)
    && (c.b == 0 || c.b == 255);
}

int main(int argc, char *argv[]) {
  RGBMatrix::Options matrix_options;
  rgb_matrix::RuntimeOptions runtime_opt;
  if (!rgb_matrix::ParseOptionsFromFlags(&argc, &argv,
                                         &matrix_options, &runtime_opt)) {
    return usage(argv[0]);
  }

  Color color(255, 255, 255);
  Color bg_color(0, 0, 0);

  /* x_origin is set by default just right of the screen */
  const int x_default_start = (matrix_options.chain_length * matrix_options.cols) + 5;
  int x_orig = x_default_start;
  int y_orig = 0;
  int brightness = 50;
  int letter_spacing = 0;
  float speed = 10.0f;
  int loops = -1;


  /*
   * Load font. This needs to be a filename with a bdf bitmap font.
   */
  rgb_matrix::Font font;
  if (!font.LoadFont("fonts/tom-thumb.bdf")) {
    fprintf(stderr, "Couldn't load font\n");
    return 1;
  }

  RGBMatrix *canvas = rgb_matrix::CreateMatrixFromOptions(matrix_options,
                                                          runtime_opt);

  if (canvas == NULL)
    return 1;

  canvas->SetBrightness(brightness);

  const bool all_extreme_colors = (brightness == 100)
    && FullSaturation(color)
    && FullSaturation(bg_color);
  if (all_extreme_colors)
    canvas->SetPWMBits(1);

  signal(SIGTERM, InterruptHandler);
  signal(SIGINT, InterruptHandler);

  printf("CTRL-C for exit.\n");

  // Create a new canvas to be used with led_matrix_swap_on_vsync
  FrameCanvas *offscreen_canvas = canvas->CreateFrameCanvas();

  int delay_speed_usec = 1000000;
  if (speed > 0) {
    delay_speed_usec = 1000000 / speed / font.CharacterWidth('W');
  } else if (x_orig == x_default_start) {
    // There would be no scrolling, so text would never appear. Move to front.
    x_orig = 0;
  }

  int x = x_orig;
  int y = y_orig;
  int length = 0;

  
  Document d;

  while (!interrupt_received && loops != 0) {
    offscreen_canvas->Fill(bg_color.r, bg_color.g, bg_color.b);
    char readBuffer[65536];
    FILE* fp = fopen("examples-api-use/testing.json", "r");
    FileReadStream is(fp, readBuffer, sizeof(readBuffer));

    d.ParseStream(is);
    fclose(fp);
    
    if(d.IsObject()) {
      assert(d.IsObject());
      assert(d.HasMember("text_display"));
      assert(d["text_display"].IsString());
      assert(d["speedconfig"].IsDouble());

      speed = d["speedconfig"].GetDouble();
    }
    

    delay_speed_usec = 1000000 / speed / font.CharacterWidth('W');

    length = rgb_matrix::DrawText(offscreen_canvas, font,
                                  x, y + font.baseline(),
                                  color, nullptr,
                                  d["text_display"].GetString(), letter_spacing);
    

    if (speed > 0 && --x + length < 0) {
      x = x_orig;
      if (loops > 0) --loops;
    }

    // Swap the offscreen_canvas with canvas on vsync, avoids flickering
    offscreen_canvas = canvas->SwapOnVSync(offscreen_canvas);
    usleep(delay_speed_usec);
  }
  
  // Finished. Shut down the RGB matrix.
  canvas->Clear();
  delete canvas;

  return 0;
}