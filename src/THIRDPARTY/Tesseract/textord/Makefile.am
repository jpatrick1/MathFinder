AM_CPPFLAGS += \
    -I$(top_srcdir)/ccstruct -I$(top_srcdir)/ccutil \
    -I$(top_srcdir)/image -I$(top_srcdir)/viewer \
    -I$(top_srcdir)/ccmain -I$(top_srcdir)/wordrec -I$(top_srcdir)/api \
    -I$(top_srcdir)/cutil -I$(top_srcdir)/classify -I$(top_srcdir)/dict
        
if VISIBILITY
AM_CPPFLAGS += -DTESS_EXPORTS \
    -fvisibility=hidden -fvisibility-inlines-hidden
endif


noinst_HEADERS = \
    alignedblob.h bbgrid.h blkocc.h blobgrid.h \
    ccnontextdetect.h cjkpitch.h colfind.h colpartition.h colpartitionset.h \
    colpartitiongrid.h \
    devanagari_processing.h drawedg.h drawtord.h edgblob.h edgloop.h \
    fpchop.h gap_map.h imagefind.h linefind.h makerow.h oldbasel.h \
    pithsync.h pitsync1.h scanedg.h sortflts.h strokewidth.h \
    tabfind.h tablefind.h tabvector.h \
    tablerecog.h textlineprojection.h textord.h \
    topitch.h tordmain.h tovars.h \
    underlin.h wordseg.h workingpartset.h

if !USING_MULTIPLELIBS
noinst_LTLIBRARIES = libtesseract_textord.la
else
lib_LTLIBRARIES = libtesseract_textord.la
libtesseract_textord_la_LDFLAGS = -version-info $(GENERIC_LIBRARY_VERSION)
libtesseract_textord_la_LIBADD = \
    ../ccstruct/libtesseract_ccstruct.la \
    ../ccutil/libtesseract_ccutil.la \
    ../image/libtesseract_image.la \
    ../viewer/libtesseract_viewer.la \
    ../wordrec/libtesseract_wordrec.la \
    ../cutil/libtesseract_cutil.la \
    ../classify/libtesseract_classify.la \
    ../dict/libtesseract_dict.la 
endif

libtesseract_textord_la_SOURCES = \
    alignedblob.cpp bbgrid.cpp blkocc.cpp blobgrid.cpp \
    ccnontextdetect.cpp cjkpitch.cpp colfind.cpp colpartition.cpp colpartitionset.cpp \
    colpartitiongrid.cpp devanagari_processing.cpp \
    drawedg.cpp drawtord.cpp edgblob.cpp edgloop.cpp \
    fpchop.cpp gap_map.cpp imagefind.cpp linefind.cpp makerow.cpp oldbasel.cpp \
    pithsync.cpp pitsync1.cpp scanedg.cpp sortflts.cpp strokewidth.cpp \
    tabfind.cpp tablefind.cpp tabvector.cpp \
    tablerecog.cpp textlineprojection.cpp textord.cpp \
    topitch.cpp tordmain.cpp tospace.cpp tovars.cpp \
    underlin.cpp wordseg.cpp workingpartset.cpp
