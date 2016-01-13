#include "itkImage.h"
#include "itkRandomImageSource.h"
#include "itkScalarImageToTextureFeaturesFilter.h"
#include "itkImageFileReader.h"
#include "itkRegionOfInterestImageFilter.h"
#include <iostream>     // std::cout
#include <fstream>      // std::ifstream  
#include <stdio.h>
#include <stdlib.h>

 
typedef itk::Image<float, 3> ImageType;


float getTextureFeature(ImageType::RegionType roi, ImageType::Pointer image, int featureTypeId)
{
    // 3 is inertia
  typedef itk::RegionOfInterestImageFilter< ImageType, ImageType > FilterType;
  FilterType::Pointer filter = FilterType::New();
  typedef itk::Statistics::ScalarImageToTextureFeaturesFilter<ImageType> TextureFilterType;
  TextureFilterType::Pointer textureFilter = TextureFilterType::New();
  textureFilter->SetNumberOfBinsPerAxis(16);
  textureFilter->SetPixelValueMinMax(0, 255);
  textureFilter->FastCalculationsOn();
  filter->SetRegionOfInterest(roi);
  filter->SetInput(image);
  textureFilter->SetInput(filter->GetOutput());
  textureFilter->Update();
 
  const TextureFilterType::FeatureValueVector* textureResult = textureFilter->GetFeatureMeans();
  // defaults to: {Energy, Entropy, InverseDifferenceMoment, Inertia, ClusterShade, ClusterProminence
  
   
  return (*textureResult)[featureTypeId];
}


 
int main(int argc, char *argv[])
{
    if(argc < 4)
    {
    std::cerr << "Usage: " << argv[0] << " Required input image and output binary path" << std::endl;
    return EXIT_FAILURE;
    }
    
    std::string inFileName = argv[1];
    std::string outFileName = argv[2];
    std::string textureFeatureTypeToUse = argv[3];
    
    int featureTypeId;
    
   
    if (textureFeatureTypeToUse == "Energy") featureTypeId = 0;
    else if (textureFeatureTypeToUse == "Entropy") featureTypeId = 1;   
    else if (textureFeatureTypeToUse == "InverseDifferenceMoment") featureTypeId = 2; 
    else if (textureFeatureTypeToUse == "Inertia") featureTypeId = 3; 
    else if (textureFeatureTypeToUse == "ClusterShade") featureTypeId = 4; 
    else if (textureFeatureTypeToUse == "ClusterProminence") featureTypeId = 5; 
        
    
    std::cout << "using texture Feature " << featureTypeId << ": " << textureFeatureTypeToUse;
    
    
    std::ofstream output (outFileName.c_str(), std::ifstream::out | std::ifstream::binary);
 
    int chunkSize = 5;
    
   
    typedef itk::ImageFileReader<ImageType> ReaderType;
    ReaderType::Pointer reader=ReaderType::New();
    reader->SetFileName(inFileName);
    reader->Update();
    ImageType::Pointer image=reader->GetOutput();
    //std::cout << (*output)[i] << std::endl;
            
    // Loop over image in chunks 
        //slide window over the entire image
   //image->GetLargestPossibleRegion().GetSize(0)-1; x++)
    
   
   ImageType::IndexType start;
   ImageType::SizeType size;
   size[0] = 5;
   size[1] = 5;
   size[2] = 5;
   
   float textureFeature;
              
   ImageType::SizeType imsize = image->GetLargestPossibleRegion().GetSize();
   std::cout << imsize << std::endl;
   
   int total = 0;
   
   float pixel;
   
   for(int x=0; x<imsize[0] - chunkSize; x += chunkSize) // for all Columns
    {
        for(int y=0; y<imsize[1] - chunkSize; y+=chunkSize) // for all Rows
        {
            
            for(int z=0; z<imsize[2]- chunkSize; z+=chunkSize) // for all Rows
            {
               start[0] = x;
               start[1] = y;
               start[2] = z;
               ImageType::RegionType desiredRegion;
               desiredRegion.SetSize(size);
               desiredRegion.SetIndex(start);
               
               textureFeature = getTextureFeature(desiredRegion, image, featureTypeId); 
               
               output.write(reinterpret_cast<const char*>(&textureFeature), sizeof(textureFeature));
               total++;
            }
        }
        
      }
   std::cout << "\n\ntotal: " << total << std::endl;
    
        
}

