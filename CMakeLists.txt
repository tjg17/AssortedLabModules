cmake_minimum_required(VERSION 2.8.9)

project(AssortedLabModules)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "http://www.example.com/Slicer/Extensions/AssortedLabModules")
set(EXTENSION_CATEGORY "Examples")
set(EXTENSION_CONTRIBUTORS "Tyler Glass (Nightingale Lab)")
set(EXTENSION_DESCRIPTION "This extension contains assorted modules used to perform tasks for Nightingale Lab research.")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/AssortedLabModules.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/AssortedLabModules/Screenshots/1.png")

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(SetVolumeScalars)
add_subdirectory(VisualizeTimesteps)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_CPACK})
