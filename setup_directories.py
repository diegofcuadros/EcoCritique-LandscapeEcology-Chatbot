#!/usr/bin/env python3
"""
Setup script for EcoCritique - Creates required directories and initializes basic structure
Run this script once before first deployment or when setting up a new environment
"""

import os
import sys

def create_directories():
    """Create all required directories for the EcoCritique application"""
    
    directories = [
        "data",                    # Database and knowledge base files
        "article_research",        # Research agent output
        "uploads",                 # Temporary file uploads
        "exports",                 # Exported data files
        "logs",                    # Application logs (if needed)
        "data/cache",             # Caching directory
        ".streamlit"              # Streamlit configuration (if not exists)
    ]
    
    created_dirs = []
    skipped_dirs = []
    
    for directory in directories:
        try:
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                created_dirs.append(directory)
                print(f"[+] Created directory: {directory}")
            else:
                skipped_dirs.append(directory)
                print(f"[i] Directory already exists: {directory}")
                
        except Exception as e:
            print(f"[!] Failed to create directory {directory}: {e}")
            return False
    
    print(f"\nDirectory setup complete!")
    print(f"   Created: {len(created_dirs)} new directories")
    print(f"   Existing: {len(skipped_dirs)} directories")
    
    return True

def create_basic_knowledge_base():
    """Create a basic landscape ecology knowledge base if it doesn't exist"""
    
    kb_path = "data/landscape_ecology_kb.txt"
    
    if os.path.exists(kb_path):
        print(f"[i] Knowledge base already exists: {kb_path}")
        return True
    
    try:
        basic_kb_content = """# Landscape Ecology Knowledge Base

## Core Concepts

### Scale and Hierarchy
Landscape ecology operates across multiple spatial and temporal scales. Understanding scale effects is crucial for interpreting ecological patterns and processes. Grain refers to the smallest unit of observation, while extent defines the total area or time period of study.

### Spatial Pattern and Process
The relationship between spatial patterns and ecological processes is fundamental to landscape ecology. Patterns at one scale often reflect processes operating at different scales. Pattern-process relationships help us understand how landscape structure influences ecological function.

### Habitat Fragmentation
Habitat fragmentation involves both habitat loss and the subdivision of remaining habitat into smaller, more isolated patches. This process affects species diversity, population dynamics, and ecosystem processes through reduced patch size, increased edge effects, and decreased connectivity.

### Landscape Connectivity
Connectivity describes the degree to which landscapes facilitate or impede ecological flows such as movement of organisms, materials, or energy. Structural connectivity refers to the physical arrangement of landscape elements, while functional connectivity considers how organisms actually use the landscape.

### Edge Effects
Edge effects occur at the boundaries between different habitat types or landscape elements. These edges often have different environmental conditions, species composition, and ecological processes compared to habitat interiors. Edge effects can extend significant distances into habitat patches.

### Metapopulation Dynamics
Metapopulation theory describes how local populations connected by migration can persist through a balance of local extinctions and recolonizations. This framework is particularly relevant for understanding species persistence in fragmented landscapes.

### Disturbance Regimes
Disturbances are discrete events that disrupt ecosystems and create spatial and temporal heterogeneity. Natural disturbances include fire, windstorms, flooding, and disease outbreaks. The frequency, intensity, and spatial pattern of disturbances shape landscape patterns.

### Landscape Heterogeneity
Spatial heterogeneity refers to the uneven distribution of habitats, resources, or environmental conditions across landscapes. Heterogeneity is important for maintaining biodiversity and providing diverse ecological niches.

### Conservation Applications
Landscape ecology principles are widely applied in conservation biology, restoration ecology, and landscape planning. Understanding landscape patterns and processes is essential for effective conservation strategies and sustainable land management.

## Research Methods

### Remote Sensing and GIS
Remote sensing and Geographic Information Systems (GIS) are fundamental tools in landscape ecology. They enable analysis of landscape patterns across large spatial extents and long time periods. Common applications include land cover classification, change detection, and spatial analysis.

### Landscape Metrics
Quantitative measures of landscape structure include metrics of composition (what is present) and configuration (spatial arrangement). Common metrics include patch size, edge density, connectivity indices, and diversity measures.

### Field Studies
Field research validates remote sensing analyses and provides detailed ecological data. Field studies often focus on how landscape patterns affect species distributions, population dynamics, and ecological processes.

### Modeling Approaches
Landscape ecology employs various modeling approaches including spatially explicit population models, landscape change models, and process-based ecosystem models. These models help predict landscape dynamics and species responses to environmental change.

## Case Studies and Applications

### Forest Fragmentation Studies
Classic studies in forest landscapes have documented how fragmentation affects bird communities, plant populations, and ecosystem processes. These studies demonstrate the importance of patch size, edge effects, and connectivity for maintaining forest biodiversity.

### Urban Landscape Ecology
Urban landscapes present unique challenges and opportunities for ecological research. Urban ecology examines how urbanization affects ecological processes and how green infrastructure can maintain ecological connectivity in human-dominated landscapes.

### Agricultural Landscapes
Agricultural landscapes are among the most extensive human-modified environments. Research focuses on how farming practices affect biodiversity, ecosystem services, and landscape connectivity. Agroecological approaches seek to enhance ecological function in agricultural systems.

### Aquatic Landscape Ecology
Aquatic systems are increasingly viewed from a landscape perspective. Stream networks, wetland complexes, and lake districts are analyzed as interconnected landscape elements. Watershed-scale approaches are essential for understanding aquatic ecosystem function.

## Current Research Frontiers

### Climate Change and Landscape Ecology
Climate change is altering landscape patterns and ecological processes worldwide. Research focuses on how species and ecosystems will respond to changing climate conditions and how landscape connectivity can facilitate adaptation.

### Landscape Genetics
The field of landscape genetics combines landscape ecology with population genetics to understand how landscape features affect gene flow and population structure. This approach provides insights into population connectivity and evolutionary processes.

### Ecosystem Services and Landscapes
Ecosystem services research examines how landscape patterns affect the provision of services such as carbon storage, water purification, and pollination. This work informs landscape planning and management for human well-being.

### Social-Ecological Systems
Landscape ecology increasingly recognizes the coupled nature of human and natural systems. Social-ecological research examines how human activities and ecological processes interact across landscapes and how this understanding can inform sustainable management.

## Synthesis and Integration

### Transdisciplinary Approaches
Modern landscape ecology is inherently transdisciplinary, integrating knowledge from ecology, geography, remote sensing, social sciences, and other fields. This integration is essential for addressing complex environmental challenges.

### Scale Integration
A major challenge in landscape ecology is integrating across scales from local ecological processes to regional and global patterns. Multi-scale approaches are needed to understand how processes operating at different scales interact.

### Applied Landscape Ecology
Landscape ecology has strong applied dimensions in conservation biology, restoration ecology, urban planning, and natural resource management. The field's emphasis on spatial patterns and processes provides practical insights for landscape management and policy.
"""
        
        with open(kb_path, 'w', encoding='utf-8') as f:
            f.write(basic_kb_content)
        
        print(f"[+] Created basic knowledge base: {kb_path}")
        print(f"   Content length: {len(basic_kb_content)} characters")
        return True
        
    except Exception as e:
        print(f"[!] Failed to create knowledge base: {e}")
        return False

def create_streamlit_config():
    """Create basic Streamlit configuration if needed"""
    
    config_path = ".streamlit/config.toml"
    
    if os.path.exists(config_path):
        print(f"[i] Streamlit config already exists: {config_path}")
        return True
    
    try:
        config_content = """[theme]
primaryColor = "#2E8B57"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F8FF"
textColor = "#262730"

[server]
maxUploadSize = 50
enableCORS = false
enableWebsocketCompression = false

[browser]
gatherUsageStats = false
"""
        
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(config_content)
        
        print(f"[+] Created Streamlit config: {config_path}")
        return True
        
    except Exception as e:
        print(f"[!] Failed to create Streamlit config: {e}")
        return False

def main():
    """Main setup function"""
    
    print("EcoCritique Setup Script")
    print("=" * 40)
    
    success = True
    
    # Create directories
    print("Creating directory structure...")
    if not create_directories():
        success = False
    
    print("\nSetting up knowledge base...")
    if not create_basic_knowledge_base():
        success = False
    
    print("\nCreating configuration files...")
    if not create_streamlit_config():
        success = False
    
    print("\n" + "=" * 40)
    
    if success:
        print("Setup completed successfully!")
        print("\nNext steps:")
        print("   1. Configure API keys in your deployment environment")
        print("   2. Upload your first article via the Professor Dashboard")
        print("   3. Test the application with a student account")
        return 0
    else:
        print("Setup completed with errors!")
        print("   Please check the error messages above and retry.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)