/**************************************************************************
 * File name:   HeuristicMerge.h
 * Written by:  Jake Bruce, Copyright (C) 2013
 * History:     Created Oct 27, 2013 1:29:14 AM
 *              Updated Oct 30, 2016
 ***************************************************************************/
#ifndef HEURISTICMERGE_H
#define HEURISTICMERGE_H

#include <Seg.h>
#include <FeatExt.h>
#include <MFinderResults.h>
#include <BlobDataGrid.h>
#include <BlobData.h>
#include <Direction.h>
#include <AlignedFeatExt.h>
#include <StackedFeatExt.h>
#include <OtherRec.h>

#include <allheaders.h>

#include <vector>
#include <string>

class HeuristicMerge : public virtual MathExpressionSegmentor {
 public:
  HeuristicMerge(MathExpressionFeatureExtractor* const featureExtractor);

  void runSegmentation(BlobDataGrid* grid);

  ~HeuristicMerge();

 private:
  void setDbgImg(Pix* im);
  void decideAndMerge(BlobData* blob, const int& seg_id);
  void mergeDecision(BlobData* blob, BlobSpatial::Direction dir);
  BlobData* lookForHorizontalMerge(TBOX* const segmentBox,
      BlobDataGrid* const blobDataGrid, BlobSpatial::Direction dir, const int& segId);
  void checkIntersecting(BlobData* blob);
  void mergeOperation(BlobData* merge_from, BlobData* to_merge,
      BlobSpatial::Direction merge_dir);

  bool isOperator(BlobData* blob);
  bool wasAlreadyMerged(BlobData* neighbor, BlobData* blob);
  bool isHorizontal(BlobSpatial::Direction dir);

  /**
   * Gets a list of all of the blobs having the same parent as the given blob
   * (includes the blob itself in the list)
   */
  std::vector<BlobData*> getBlobsWithSameParent(BlobData* const blobData);

  /**
   * Gets the feature extractor with the given name if exists. If not then creates it.
   * Caller has to cast back to correct type.
   */
  BlobFeatureExtractor* getFeatureExtractor(const std::string& name);

  /**
   * Filters out the blobs in the input vector that were already merged
   * to some other segmentation (their segmentation data structure has
   * already been assigned an id).
   */
  GenericVector<BlobData*> filterAlreadyMerged(
      const GenericVector<BlobData*> blobs);

  MathExpressionFeatureExtractor* featureExtractor;

  Pix* dbgim;

  NumAlignedBlobsFeatureExtractor* numAlignedBlobsFeatureExtractor;
  NumVerticallyStackedBlobsFeatureExtractor* numVerticallyStackedFeatureExtractor;
  OtherRecognitionFeatureExtractor* otherFeatureExtractor;
  BlobDataGrid* blobDataGrid;

  const float highCertaintyThresh;

  int mergeRecursions;
};

#endif
