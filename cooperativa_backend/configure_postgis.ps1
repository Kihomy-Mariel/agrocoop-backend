# Configuración de Variables de Entorno para PostGIS
# Ejecutar este script antes de usar Django con PostGIS

# Configurar PATH para incluir OSGeo4W
$env:PATH = "C:\OSGeo4W\bin;C:\OSGeo4W\apps\qgis\bin;" + $env:PATH

# Configurar bibliotecas GDAL y GEOS
$env:GDAL_LIBRARY_PATH = "C:\OSGeo4W\bin\gdal311.dll"
$env:GEOS_LIBRARY_PATH = "C:\OSGeo4W\bin\geos_c.dll"

# Configurar datos de GDAL y PROJ
$env:GDAL_DATA = "C:\OSGeo4W\share\gdal"
$env:PROJ_LIB = "C:\OSGeo4W\share\proj"

Write-Host "Variables de entorno configuradas para PostGIS"