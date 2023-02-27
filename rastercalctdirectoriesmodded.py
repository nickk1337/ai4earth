import os
import pandas as pd


for years in range (2017, 2022):
    directory = 'C:/Users/MLMan/Desktop/Landsat Download/' + str(years) + '/'
    iterator = os.walk(directory)
    for root, subdirectories, files in iterator:
        for subdirectory in subdirectories:
            a = os.path.join(root, subdirectory)
            a = a.replace('\\', '/')
            b = a.replace('Landsat', 'SMAP')
            lyr2 = QgsRasterLayer(a + '/' + subdirectory + '_B2.tif')
            lyr3 = QgsRasterLayer(a + '/' + subdirectory + '_B3.tif')
            lyr4 = QgsRasterLayer(a + '/' + subdirectory + '_B4.tif')
            lyr5 = QgsRasterLayer(a + '/' + subdirectory + '_B5.tif')

            si_in = []

            for i in range(1, 11):
                op = b + '/' + 'SI' + str(i) + '.tif'
                si_in.append(op)

            entries = []

            ras = QgsRasterCalculatorEntry()
            ras.ref = 'ras@2'
            ras.raster = lyr2
            ras.bandNumber = 1
            entries.append(ras)

            ras = QgsRasterCalculatorEntry()
            ras.ref = 'ras@3'
            ras.raster = lyr3
            ras.bandNumber = 1
            entries.append(ras)

            ras = QgsRasterCalculatorEntry()
            ras.ref = 'ras@4'
            ras.raster = lyr4
            ras.bandNumber = 1
            entries.append(ras)

            ras = QgsRasterCalculatorEntry()
            ras.ref = 'ras@5'
            ras.raster = lyr5
            ras.bandNumber = 1
            entries.append(ras)

            input = []
            input.append('sqrt(ras@2 * ras@4)')
            input.append('sqrt(ras@3 * ras@4)')
            input.append('sqrt((ras@3 * ras@3) + (ras@4 * ras@4))')
            input.append('(ras@2 * ras@4) / ras@3')
            input.append('(ras@3 + ras@4) / 2')
            input.append('ras@2 / ras@4')
            input.append('(ras@2 - ras@4) / (ras@2 + ras@4)')
            input.append('(ras@3 * ras@4) / ras@2')
            input.append('((ras@4 * ras@5) / ras@3)')
            input.append('sqrt((ras@4 * ras@4) + (ras@3 * ras@3) + (ras@5 * ras@5))')

            for i in range(0, 10):
                calc = QgsRasterCalculator(input[i], si_in[i], 'GTiff', lyr2.extent(), lyr2.width(), lyr2.height(),
                                           entries)
                calc.processCalculation()

            nc_file_loc = b
            nc_file_name = subdirectory + '.nc":sss_smap'
            nc_file_in = 'NETCDF:"' + nc_file_loc + '/' + nc_file_name
            vrt_in = nc_file_loc + '/' + nc_file_name[:-13] + '.vrt'
            xyz = nc_file_loc + '/' + nc_file_name[:-13] + '.xyz'
            sample_in = 'delimitedtext://file:///' + xyz + '?type=csv&useHeader=No&maxFields=10000&detectTypes=yes&xField=field_1&yField=field_2&crs=EPSG:4326&spatialIndex=no&subsetIndex=no&watchFile=no'

            output_csv = []
            print(nc_file_in)

            for i in range(1, 11):
                op = b + '/' + 'SI' + str(i) + 'sample.csv'
                output_csv.append(op)

            iface.addRasterLayer(nc_file_in, )
            processing.run("gdal:buildvirtualraster",
                           {'INPUT': [nc_file_in], 'RESOLUTION': 0, 'SEPARATE': False, 'PROJ_DIFFERENCE': True,
                            'ADD_ALPHA': False, 'ASSIGN_CRS': QgsCoordinateReferenceSystem('EPSG:4326'),
                            'RESAMPLING': 0, 'SRC_NODATA': '', 'EXTRA': '', 'OUTPUT': vrt_in})
            processing.run("grass7:r.out.xyz", {'input': [vrt_in], 'separator': ',', '-i': False, 'output': xyz,
                                                'GRASS_REGION_PARAMETER': None, 'GRASS_REGION_CELLSIZE_PARAMETER': 0})
            for j in range(0, 10):
                processing.run("native:rastersampling",
                               {'INPUT': sample_in, 'RASTERCOPY': si_in[j], 'COLUMN_PREFIX': ('SI' + str(j + 1)),
                                'OUTPUT': output_csv[j]})
                os.remove(si_in[j])

            export_loc = 'C:/Users/MLMan/Desktop/CSVs/'

            df1 = pd.read_csv(output_csv[0], header=None)
            df1 = df1.dropna()
            df1 = df1.loc[(df1 != 0).any(axis=1)]

            for j in range(1, 10):
                df2 = pd.read_csv(output_csv[j], header=None)
                df2 = df2.dropna()
                df2 = df2.loc[(df2 != 0).any(axis=1)]
                df1['SI' + str(j + 1)] = df2[3]

            df1 = df1.iloc[:, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]]
            df1 = df1.drop(0)
            df1.rename(
                columns={0: 'Longitude', 1: 'Latitude', 2: 'SSS', 3: 'SI1', 4: 'SI2', 5: 'SI3', 6: 'SI4', 7: 'SI5',
                         8: 'SI6', 9: 'SI7', 10: 'SI8', 11: 'SI9', 12: 'SI10'}, inplace=True)
            df1 = df1.dropna()
            df1.to_csv(export_loc + subdirectory + '.csv', header=True,
                       index=False)