CXXFLAGS=-Wall -O3 -g
OBJECTS=nhlrenderer.o
BINARIES=nhlrenderer

RGB_INCDIR=submodules/matrix/include
RGB_LIBDIR=submodules/matrix/lib
RGB_LIBRARY_NAME=rgbmatrix
RGB_LIBRARY=$(RGB_LIBDIR)/lib$(RGB_LIBRARY_NAME).a

$(RGB_LIBRARY):
	$(MAKE) -C $(RGB_LIBDIR)


REND_INCDIR=src/cpp/include
#REND_LIBDIR=pp-server/lib
REND_LIBRARY_NAME=nhlrenderer
REND_LIBRARY=$(REND_LIBDIR)/lib$(REND_LIBRARY_NAME).a

LDFLAGS+=-L$(REND_LIBDIR) -l$(REND_LIBRARY_NAME) \
         -L$(RGB_LIBDIR) -l$(RGB_LIBRARY_NAME) \
          -lrt -lm -lpthread

all : nhlrenderer

nhlrenderer : $(OBJECTS) $(RGB_LIBRARY) $(PP_LIBRARY)
	$(CXX) $(CXXFLAGS) $(OBJECTS) -o $@ $(LDFLAGS)

$(RGB_LIBRARY): FORCE
	$(MAKE) -C $(RGB_LIBDIR)

$(REND_LIBRARY): FORCE
	$(MAKE) -C $(REND_LIBDIR)

nhlrenderer.o : nhlrenderer.cc

%.o : %.cc
	$(CXX) -I$(REND_INCDIR) -I$(RGB_INCDIR) $(CXXFLAGS) -c -o $@ $<

clean:
	rm -f $(OBJECTS) $(BINARIES)
	$(MAKE) -C $(RGB_LIBDIR) clean
	$(MAKE) -C $(REND_LIBDIR) clean

FORCE:
.PHONY: FORCE