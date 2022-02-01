#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PyKOALA: KOALA data processing and analysis 
# by Angel Lopez-Sanchez, Yago Ascasibar, Pablo Corcho-Caballero
# Extra work by Ben Lawson (MQ PACE student)
# Plus Taylah Beard and Matt Owers (sky substraction)
# Documenting: Nathan Pidcock, Giacomo Biviano, Jamila Scammill, Diana Dalae, Barr Perez
# version = "It will read it from the PyKOALA code..."
# This is Python 3.7
# To convert to Python 3 run this in a command line :
# cp PyKOALA_2021_02_02.py PyKOALA_2021_02_02_P3.py
# 2to3 -w PyKOALA_2021_02_02_P3.py
# Edit the file replacing:
#                 exec('print("    {:2}       {:18.12f}   {:18.12f}        {:4.1f}        {:5.2f}".format(i+1, '+cube_aligned_object[i]+'.RA_centre_deg,'+cube_aligned_object[i]+'.DEC_centre_deg,'+cube_aligned_object[i]+'.pixel_size_arcsec,'+cube_aligned_object[i]+'.kernel_size_arcsec))')

# This is the first full version of the code DIVIDED


# -----------------------------------------------------------------------------
# Start timer
# -----------------------------------------------------------------------------
from timeit import default_timer as timer    
start = timer()
# -----------------------------------------------------------------------------
# Import PyKOALA
# -----------------------------------------------------------------------------
#import PyKOALA_2021_02_02 as PK    # This will NOT import variables and all tasks 
                                    # would need to be called using PK.task() ....
#exec(compile(open('PyKOALA_2021_02_13_P3.py', "rb").read(), 'PyKOALA_2021_02_13_P3.py', 'exec'))   # This just reads the file. 
                                    # If the PyKOALA code is not changed, there is no need of reading it again


pykoala_path = "/DATA/KOALA/Python/GitHub/koala/src/koala/"



# 0. Read __init__ with the version ( or file version.txt )
# version="Version 1.1 - 25 January 2022 - First one AFTER breaking the code"
with open(pykoala_path+'version.txt') as f:
    version = f.read()

# 1. Add file with constant data
exec(compile(open(pykoala_path+"constants.py", "rb").read(), pykoala_path+"constants.py", 'exec'))   # This just reads the file. 
#from pykoala import constants 

# 2. Add file with I/O tasks
exec(compile(open(pykoala_path+"io.py", "rb").read(), pykoala_path+"io.py", 'exec'))   
# #from pykoala import io 

# 3. Add file with plot_plot and basic_statistics (task included in plot_plot.py)
exec(compile(open(pykoala_path+"plot_plot.py", "rb").read(), pykoala_path+"plot_plot.py", 'exec'))   
# #from pykoala import plot_plot as plot_plot

# 4. Add file with 1D spectrum tasks
exec(compile(open(pykoala_path+"onedspec.py", "rb").read(), pykoala_path+"onedspec.py", 'exec'))  
#from pykoala import onedspec 

# 5. Add file with RSS class & RSS tasks
exec(compile(open(pykoala_path+"rss.py", "rb").read(), pykoala_path+"rss.py", 'exec'))   

# 5. Add file with KOALA_RSS class & KOALA_RSS specific tasks
exec(compile(open(pykoala_path+"koala_rss.py", "rb").read(), pykoala_path+"koala_rss.py", 'exec'))   

# 7. Add file with Interpolated_cube class & cube specific tasks
exec(compile(open(pykoala_path+"cube.py", "rb").read(), pykoala_path+"cube.py", 'exec'))   

# 8. Add the 4 AUTOMATIC SCRIPTS 
exec(compile(open(pykoala_path+"automatic_scripts/automatic_calibration_night.py", "rb").read(), pykoala_path+"automatic_scripts/automatic_calibration_night.py", 'exec'))   

exec(compile(open(pykoala_path+"automatic_scripts/run_automatic_star.py", "rb").read(), pykoala_path+"automatic_scripts/run_automatic_star.py", 'exec'))   

exec(compile(open(pykoala_path+"automatic_scripts/automatic_koala_reduce.py", "rb").read(), pykoala_path+"automatic_scripts/automatic_koala_reduce.py", 'exec'))   

exec(compile(open(pykoala_path+"automatic_scripts/koala_reduce.py", "rb").read(), pykoala_path+"automatic_scripts/koala_reduce.py", 'exec'))   



# -----------------------------------------------------------------------------
# -----------------------------------------------------------------------------

if __name__ == "__main__":

    print("\n> Testing PyKOALA. Running", version)
      
    
    # # First, copy the input data to a local folder (not within PyKOALA)

    # # Type where your data will be:
    path = "/DATA/KOALA/Python/GitHub/test_reduce/"             
    #os.system("mkdir "+path)
    #os.system("cp -R ./input_data/sample_RSS/* "+path)

    # # For AAOmega, we have TWO folders per night: blue (580V) and red (385R)

    path_red = path+"385R/"
    path_blue = path+"580V/"

    # # -----------------------------------------------------------------------
    # # -----------------------------------------------------------------------
    # # Now, it is recommended to first process the RED data
    # # -----------------------------------------------------------------------
    # # -----------------------------------------------------------------------

    # # List the files in the folder
    list_fits_files_in_folder(path_red)
    
    # PyKOALA finds 4 objects: HD60753, HILT600 (calibration stars),
    #                          He2-10 (the galaxy),
    #                          SKYFLAT
    
    # # -----------------------------------------------------------------------

    # # Next, run this for AUTOMATICALLY processing calibration of the night
    #automatic_calibration_night(path=path_red, auto=True) 
                                #, kernel_throughput = 21)
 
    
    # # This will create 2 (3 for red) files needed for the calibration:
    
    # # 1. The throughput_2D_file:
    throughput_2D_file = path_red+"throughput_2D_20180227_385R.fits"
    # # 2. The flux calibration file:
    flux_calibration_file = path_red+"flux_calibration_20180227_385R_0p7_1k10.dat"
    # # 3. The telluric correction file (only in red):
    telluric_correction_file = path_red+"telluric_correction_20180227_385R.dat"
    
    # # It will also create 2 Python objects:
    # # HD60753_385R_20180227 : Python object with calibration star HD60753
    # # Hilt600_385R_20180227 : Python object with calibration star Hiltner 600
    
    # # Run automatic calibration when throughput 2D has been obtained:
    # automatic_calibration_night(path=path_red, auto=True, 
    #                             throughput_2D_file=throughput_2D_file)
    
    
    # # Run automatic calibration when throughput 2D has been obtained
    # # AND 2 Python objects (only for checking FLUX calibration)
    # # In this case, adding abs_flux_scale =[1.1, 1.0],
    # # as HD60753 does not work as well as Hilt600
    
    # automatic_calibration_night(path=path_red, auto=True, 
    #                             #list_of_objects =["Hilt600_385R_20180227"],
    #                             #star_list =["Hilt600"],
    #                             grating="385R",
    #                             date="20180227",
    #                             throughput_2D_file=throughput_2D_file,
    #                             abs_flux_scale =[1.1, 1.0], # add this for SCALING stars, if needed
    #                             cal_from_calibrated_starcubes = True)
    
    # # -----------------------------------------------------------------------
    # # Now it is time to process an RSS file, using KOALA_RSS
    # # It is recommended to test it here BEFORE running automatic scripts
    
    
    # file_in   = path_red+"27feb20031red.fits"
    # file_med  = path_red+"27feb20031red_TCWXU____.fits"
    # file_med2 = path_red+"27feb20031red_TCWXUS___.fits"
    # file_out  = path_red+"27feb20031red_TCWXUS_NR.fits"

    # # As the critical part is the SKY SUBTRACION, first do everything till that
    
    # test = KOALA_RSS(file_in, 
    #                  save_rss_to_fits_file="auto",  
    #                  apply_throughput=True, 
    #                  throughput_2D_file=throughput_2D_file,       # if throughput_2D_file given, use SOL in fits file for fixing wave
    #                  #throughput_2D=throughput_2D_20180227_385R,
    #                  correct_ccd_defects = True, 
    #                  fix_wavelengths = True, 
    #                  #sol=[0.0853325247121367,-0.0009925545410042428,1.582994591921196e-07],
    #                  do_extinction=True,
    #                  telluric_correction_file=telluric_correction_file)

    # # This will automatically create the file "27feb20031red_TCWXU____.fits"
    
    # # Now it is time to check the sky
    # # Running just a "self" n_sky = 25, that is
    # # using the 25 fibres with LOWEST integrated values to get the sky:
    
    # test = KOALA_RSS(file_med, 
    #                  save_rss_to_fits_file="auto",  
    #                  sky_method="self", n_sky=25)
    
    # # This will create file_med2, that has keys "_TCWXUS___"
    # # Change manually the name of that file to compare in DS9 later with 
    # # the other tests we are performing (e.g. "_TCWXUSself___")
    
    # # There are some problems here:
    # # 1. H-alpha is everywhere, at ~6583. We can't use self
    # # 2. Still, many residuals after subtracting IR sky lines.

    # # Solving 1 is tricky, we should have used offset skies (2D)
    
    # # An option is getting the sky of a calibration star or a faint object 
    # # and SCALING 
    # #
    # sky1=KOALA_RSS(path_red+"27feb20030red.fits",
    #                #save_rss_to_fits_file="auto",
    #                apply_throughput=True, 
    #                throughput_2D_file=throughput_2D_file,
    #                correct_ccd_defects = True, 
    #                fix_wavelengths = True, 
    #                do_extinction=True,
    #                is_sky=True,
    #                sky_fibres= fibres_best_sky_100,
    #                plot=True, warnings=False)

    # # This will be our sky spectrum for replacing emission lines in rss
    # sky1_spec=sky1.sky_emission   
    
    # # If we provide sky_spectrum = sky1_spec, 
    # # and choose sky_method="self" or "selffit,
    # # it will run RSS task "replace_el_in_sky_spectrum"
    # # to get the sky spectrum to use.
    
    # # However this task currently DOES NOT PROPERLY WORK... it needs checking
    
    # # Let's obtain the self sky and fit a Gaussian in H-alpha:
        
    # sky1=KOALA_RSS(file_med, sky_method="self", n_sky=25)
    # sky1_spec=sky1.sky_emission 
    # w=test.wavelength
    # plot_plot(w,sky1_spec, vlines=[6583], xmin=6500, xmax=6650)
    
    # fluxes(w,sky1_spec ,6584, lowlow=50,lowhigh=30, highlow=30,highhigh=50, broad=1.5)
    # # Fails with a single Gaussian fit, trying a double Gaussian fit:
    # dfluxes(w,sky1_spec ,6577,6584, lowlow=50,lowhigh=30, highlow=30,highhigh=50)
    # # With this, x0, y0, sigma  = 6583.768393198269, 91.05682233417284, 2.1031790823208825
    # gaussHa = gauss(w, 6583.768393198269, 91.05682233417284, 2.1031790823208825)
    # sky1_spec_good = sky1_spec-gaussHa
    # plot_plot(w,[sky1_spec,gaussHa, sky1_spec_good], vlines=[6584], xmin=6500, xmax=6650,
    #           ptitle="Subtracting H-alpha to the sky emission", ymin=-20, ymax=600)
    
    # # For solving 2, it is recommended to individually fit the sky lines
    # # using Gaussians, applying sky_method="selffit"
    # # and using file "sky_lines_IR_short"  (we call it with "IRshort")
    # # We also need to add parameter brightest_line_wavelength
    # # with the OBSERVED H-alpha wavelength, around 6583

    # test = KOALA_RSS(file_med, 
    #                   save_rss_to_fits_file="auto",  
    #                   sky_spectrum = sky1_spec_good,
    #                   sky_method="1Dfit",
    #                   scale_sky_1D = 1.0,
    #                   brightest_line = "Ha",
    #                   brightest_line_wavelength = 6583,
    #                   sky_lines_file="IRshort")

    # # Don't forget to save the sky as a 1D fits file or text file:
    # spectrum_to_text_file(w, sky1_spec_good, filename=path_red+"27feb20031red_sky.txt", verbose=True )

    # # Finally, we can clean a bit more the sky residuals
    
    # test = KOALA_RSS(file_med2, 
    #                   save_rss_to_fits_file="auto",  
    #                   correct_negative_sky = True, 
    #                   order_fit_negative_sky = 7, kernel_negative_sky=51, individual_check=True, 
    #                   use_fit_for_negative_sky=True, force_sky_fibres_to_zero=True,
    #                   remove_negative_median_values = True,
    #                   clean_sky_residuals = True, features_to_fix = "big_telluric",
    #                   fix_edges = True,
    #                   clean_extreme_negatives=True, percentile_min=0.9,
    #                   clean_cosmics=True,
    #                   width_bl=0., kernel_median_cosmics=5, cosmic_higher_than = 100., extra_factor =	2.)
    
    # # We can compare what we have done opening the files in DS9 or running this:
    
    # print("\n\n - Plotting original RSS:")
    # test = KOALA_RSS(file_in, verbose=False)
    # print(" - Plotting RSS corrected by TCWXU:")
    # test = KOALA_RSS(file_med, verbose=False)
    # print(" - Plotting RSS corrected by TCWXU and 1Dfit sky:")
    # test = KOALA_RSS(file_med2, verbose=False)
    # print(" - Plotting RSS corrected by TCWXU, 1Dfit sky, and sky residuals:")
    # test = KOALA_RSS(file_out, verbose=False)

    # # If we have had the sky spectrum, we could have done it everything together:
        
    # test = KOALA_RSS(file_in, 
    #                  save_rss_to_fits_file="auto",  
    #                  apply_throughput=True, 
    #                  throughput_2D_file=throughput_2D_file,       # if throughput_2D_file given, use SOL in fits file for fixing wave
    #                  #throughput_2D=throughput_2D_20180227_385R,
    #                  correct_ccd_defects = True, 
    #                  fix_wavelengths = True, 
    #                  #sol=[0.0853325247121367,-0.0009925545410042428,1.582994591921196e-07],
    #                  do_extinction=True,
    #                  telluric_correction_file=telluric_correction_file,
    #                  sky_spectrum = sky1_spec_good,
    #                  #sky_spectrum_file = path_red+"27feb20031red_sky.txt",
    #                  sky_method="1Dfit",
    #                  scale_sky_1D = 1.0,
    #                  brightest_line = "Ha",
    #                  brightest_line_wavelength = 6583,
    #                  sky_lines_file="IRshort",
    #                  correct_negative_sky = True, 
    #                  order_fit_negative_sky = 7, kernel_negative_sky=51, individual_check=True, 
    #                  use_fit_for_negative_sky=True, force_sky_fibres_to_zero=True,
    #                  remove_negative_median_values = True,
    #                  clean_sky_residuals = True, features_to_fix = "big_telluric",
    #                  fix_edges = True,
    #                  clean_extreme_negatives=True, percentile_min=0.9,
    #                  clean_cosmics=True,
    #                  width_bl=0., kernel_median_cosmics=5, cosmic_higher_than = 100., extra_factor =	2.,
    #                  plot_final_rss = True,
    #                  plot=True, warnings=False, verbose=True)
    

    # # Now we need to repeat for the remaining 5 files of He 2-10.
    # # Again, the critical part is the SKY SUBTRACTION!
    # # As we are doing the Gaussian fit,  we first need to process TCWXU,
    # # then extract self sky, fit Gaussian (double),
    # # and then running again KOALA_RSS with 1Dfit and residuals
    
    # # It's the same for the 5 files, just comment and uncomment these as needed
    
    # file_in   = path_red+"27feb20032red.fits"
    # file_med  = path_red+"27feb20032red_TCWXU____.fits"
    # file_sky  = path_red+"27feb20032red_sky.txt"

    # file_in   = path_red+"27feb20033red.fits"
    # file_med  = path_red+"27feb20033red_TCWXU____.fits"
    # file_sky  = path_red+"27feb20033red_sky.txt"
    
    # file_in   = path_red+"27feb20034red.fits"
    # file_med  = path_red+"27feb20034red_TCWXU____.fits"
    # file_sky  = path_red+"27feb20034red_sky.txt"

    # file_in   = path_red+"27feb20035red.fits"
    # file_med  = path_red+"27feb20035red_TCWXU____.fits"
    # file_sky  = path_red+"27feb20035red_sky.txt"
    
    # file_in   = path_red+"27feb20036red.fits"
    # file_med  = path_red+"27feb20036red_TCWXU____.fits"
    # file_sky  = path_red+"27feb20036red_sky.txt"
    
    # test = KOALA_RSS(file_in, 
    #                   save_rss_to_fits_file="auto",  
    #                   apply_throughput=True, 
    #                   throughput_2D_file=throughput_2D_file,       # if throughput_2D_file given, use SOL in fits file for fixing wave
    #                   correct_ccd_defects = True, 
    #                   fix_wavelengths = True, 
    #                   do_extinction=True,
    #                   telluric_correction_file=telluric_correction_file)
  

    # sky = KOALA_RSS(file_med, sky_method="self", n_sky=25)
    # sky_spec=sky.sky_emission     
    # dfluxes(w,sky_spec ,6577,6584, lowlow=50,lowhigh=30, highlow=30,highhigh=50)

    # For file 32:  x0, y0, sigma  = 6583.816181485515 97.79633090010093 2.1633059703557453
    # gaussHa = gauss(w, 6583.816181485515, 97.79633090010093, 2.1633059703557453)
    # For file 33:  x0, y0, sigma  = 6583.318685704395 118.9126748043965 2.3678850517593446
    # gaussHa = gauss(w, 6583.318685704395, 118.9126748043965, 2.3678850517593446)
    # For file 34:  x0, y0, sigma  = 6583.38576024161 113.68364263932791 2.0602389430115675
    # gaussHa = gauss(w, 6583.38576024161, 113.68364263932791, 2.0602389430115675)
    # For file 35:  x0, y0, sigma  = 6583.320956824095 117.5123159875465 2.19115121698132
    # gaussHa = gauss(w, 6583.320956824095, 117.5123159875465, 2.19115121698132)
    # For file 36:  x0, y0, sigma  = 6583.092264772729 120.6800674492026 2.2647860224835306
    # gaussHa = gauss(w, 6583.092264772729, 120.6800674492026, 2.2647860224835306)

    # sky_spec_good = sky_spec-gaussHa
    # plot_plot(w,[sky_spec,gaussHa, sky_spec_good], vlines=[6584], xmin=6500, xmax=6650,
    #           ptitle="Subtracting H-alpha to the sky emission", ymin=-20, ymax=600)    
    
    # spectrum_to_text_file(w, sky_spec_good, filename=file_sky, verbose=True )
    
    # test = KOALA_RSS(file_med, 
    #                   save_rss_to_fits_file="auto",  
    #                   #sky_spectrum = sky_spec_good,
    #                   sky_spectrum_file = file_sky,
    #                   sky_method="1Dfit",
    #                   scale_sky_1D = 1.0,
    #                   brightest_line = "Ha",
    #                   brightest_line_wavelength = 6583,
    #                   sky_lines_file="IRshort",
    #                   correct_negative_sky = True, 
    #                   order_fit_negative_sky = 7, kernel_negative_sky=51, individual_check=True, 
    #                   use_fit_for_negative_sky=True, force_sky_fibres_to_zero=True,
    #                   remove_negative_median_values = True,
    #                   clean_sky_residuals = True, features_to_fix = "big_telluric",
    #                   fix_edges = True,
    #                   clean_extreme_negatives=True, percentile_min=0.9,
    #                   clean_cosmics=True,
    #                   width_bl=0., kernel_median_cosmics=5, cosmic_higher_than = 100., extra_factor =	2.,
    #                   plot_final_rss = True,
    #                   plot=True, warnings=False, verbose=True)
  

    # # -----------------------------------------------------------------------
    # # Once we have the CLEAN RSS files, we can do the cubing & combine
    # # -----------------------------------------------------------------------

    
    # # For making a cube, we call Interpolated_cube defining the
    # # pixel and kernel size and adding the flux_calibration
    
    # file_out  = path_red+"27feb20031red_TCWXUS_NR.fits"
    
    # cube_test = Interpolated_cube(file_out, 
    #                               pixel_size_arcsec=0.7,
    #                               kernel_size_arcsec=1.1,
    #                               flux_calibration_file=flux_calibration_file,
    #                               plot=True)
    
    # # For this galaxy, as it is off-center, running ADR automatically will FAIL

    # cube_test = Interpolated_cube(file_out, 
    #                               pixel_size_arcsec=0.7,
    #                               kernel_size_arcsec=1.1,
    #                               flux_calibration_file=flux_calibration_file,
    #                               ADR=True,
    #                               plot_tracing_maps=[6250,7500,9000],
    #                               plot=True)    

    # # A way of solving this is providing the SIZE of the cube:
    # cube_test = Interpolated_cube(file_out, 
    #                               pixel_size_arcsec=0.7,
    #                               kernel_size_arcsec=1.1,
    #                               flux_calibration_file=flux_calibration_file,
    #                               ADR=True,
    #                               #plot_tracing_maps=[6250,7500,9000],
    #                               size_arcsec=[60,40],
    #                               step_tracing = 10,             # Increase the number of points for tracing
    #                               kernel_tracing = 19,           # Smooth tracing for removing outliers
    #                               g2d=False, 
    #                               adr_index_fit = 3,
    #                               trim_cube = True,             # Trimming the cube
    #                               plot=True)    


    # # For combining several cubes, the best way is running KOALA_reduce:
        
    # # We first check the 3 first files    

    # # list with RSS files (no need to include path)    
    # rss_list = ["27feb20031red_TCWXUS_NR.fits","27feb20032red_TCWXUS_NR.fits","27feb20033red_TCWXUS_NR.fits"]
    
    # # Once you have run KOALA_reduced and obtained ADRs, you can copy and paste values for speeding tests

    # ADR_x_fit_list =  [[-2.3540791265017944e-12, 6.762388793515361e-08, -0.0006627297804396334, 2.1666411712553812], [-3.0634647703827036e-12, 8.407943128848677e-08, -0.0007965956049746986, 2.545773557437055], [-8.043867327151777e-13, 2.8827477735272883e-08, -0.0003496319743184722, 1.34787667608832]]
    # ADR_y_fit_list =  [[1.0585167511142714e-12, -3.972561095302862e-08, 0.00047854197119031385, -1.806746479722604], [5.712676673528853e-13, -2.7118172653512425e-08, 0.00034731129018336117, -1.322842656375085], [-1.2201306546407504e-12, 2.3629083572706315e-08, -0.00013682268516072916, 0.21158456279065121]]

    # # Same thing with offsets
    
    # offsets =  [ -0.2773903893335756 , 0.7159980346947741 , 2.6672716919949306 , 0.8808234960793637 ]
    
    # combined_cube_test=KOALA_reduce(rss_list, path=path_red, 
    #                                 fits_file="combined_cube_test_.fits",
    #                                 rss_clean=True,                 # RSS files are clean
    #                                 pixel_size_arcsec=0.7, kernel_size_arcsec=1.1,
    #                                 flux_calibration_file=flux_calibration_file,
    #                                 #size_arcsec=[60,40],
    
    #                                 #ADR=True,
    #                                 #plot_tracing_maps=[6250,7500,9000],
    #                                 #box_x=[53,64], box_y=[22,32],
    #                                 #box_x = [10,70],
    #                                 #box_y = [10,60],
    #                                 half_size_for_centroid = 0,   # Using all data for registering
    #                                 step_tracing = 20,            # Increase the number of points for tracing
    #                                 kernel_tracing = 9,           # Smooth tracing for removing outliers
    #                                 g2d=False, 
    #                                 adr_index_fit = 3,

    #                                 ADR_x_fit_list = ADR_x_fit_list,
    #                                 ADR_y_fit_list = ADR_y_fit_list,
    #                                 offsets = offsets,
                                    
    #                                 trim_cube = True,             # Trimming the cube
    #                                 scale_cubes_using_integflux = False, # Not scaling cubes using integrated flux of common region
    #                                 plot= True, 
    #                                 plot_rss=False, 
    #                                 plot_weight=False,
    #                                 plot_spectra = False,
    #                                 fig_size=12,
    #                                 warnings=False, verbose = True)
  
    # # Plotting a larger map without plot_spaxel_grid, contours, or grid  
  
    # combined_cube_test.combined_cube.plot_map(log=True, cmap=fuego_color_map, fig_size=20, 
                                              # plot_centre=False, plot_spaxel_grid = False, 
                                              # contours= False, alpha_grid=0, fraction =0.027)
    

    # # Now we check the 3 last files    

    # # list with RSS files (no need to include path)    
    # rss_list = ["27feb20034red_TCWXUS_NR.fits","27feb20035red_TCWXUS_NR.fits","27feb20036red_TCWXUS_NR.fits"]
    
    # # For these, there is a star in the bottom left corner we can use for aligning / ADR
    # # g2d=True # it is a star
    # # box_x=[3,15], box_y=[3,15] # define the box
    
    # # Once you have run KOALA_reduced and obtained ADRs, you can copy and paste values for speeding tests

    # ADR_x_fit_list =  [[9.472735325782044e-13, -1.8414272142169123e-08, 0.00010639453474275714, -0.16011731471966129], [1.8706793461446896e-12, -4.151166766143467e-08, 0.00029190493266945084, -0.6408077338639665], [-1.3780071545760161e-12, 3.170991526784723e-08, -0.0002355233904377564, 0.5627653239513558]]
    # ADR_y_fit_list =  [[-2.0911079335920793e-12, 4.703018551076634e-08, -0.00033904804410673275, 0.7771617214421154], [-2.838537640353266e-12, 6.54908082091063e-08, -0.00048530769637374164, 1.148318135983978], [-3.1271687976010236e-12, 7.140942741912648e-08, -0.0005301049734410775, 1.2753542609892792]]    

    # # Same thing with offsets
    
    # offsets =  [ 1.4239020516303178 , 0.003232821107207684 , 1.4757701790022182 , 1.495021090623025 ]
    # offsets =  [1.5, 0, 1.5, 1.5]  # Given at the telescope
    
    # combined_cube_test=KOALA_reduce(rss_list, path=path_red, 
    #                                 fits_file="combined_cube_test_2.fits",
    #                                 rss_clean=True,                 # RSS files are clean
    #                                 pixel_size_arcsec=0.7, kernel_size_arcsec=1.1,
    #                                 flux_calibration_file=flux_calibration_file,
    #                                 ADR=True,
    #                                 plot_tracing_maps=[6400], #[6250,7500,9000],
    #                                 #size_arcsec=[60,40],
    #                                 box_x=[3,15], box_y=[3,15],
    #                                 half_size_for_centroid = 0,   # Using all data for registering
    #                                 step_tracing = 20,            # Increase the number of points for tracing
    #                                 kernel_tracing = 19,           # Smooth tracing for removing outliers
    #                                 g2d=True, 
    #                                 adr_index_fit = 3,
                                    
    #                                 #ADR_x_fit_list = ADR_x_fit_list,
    #                                 #ADR_y_fit_list = ADR_y_fit_list,
    #                                 #offsets = offsets,
                                    
    #                                 trim_cube = True,             # Trimming the cube
    #                                 scale_cubes_using_integflux = False, # Not scaling cubes using integrated flux of common region
    #                                 plot= True, 
    #                                 plot_rss=False, 
    #                                 plot_weight=False,
    #                                 plot_spectra = False,
    #                                 fig_size=12,
    #                                 warnings=False, verbose = True)
  


    # Now it is time to merge the 2 sets
    # Here I'm trusting that the offset between file 33 and 34 is that given at the telescope: 18S 3E (this should be checked)
    # and put everything together:
    
    # rss_list = ["27feb20031red_TCWXUS_NR.fits","27feb20032red_TCWXUS_NR.fits","27feb20033red_TCWXUS_NR.fits",
    #             "27feb20034red_TCWXUS_NR.fits","27feb20035red_TCWXUS_NR.fits","27feb20036red_TCWXUS_NR.fits"]

    # ADR_x_fit_list =  [[-2.3540791265017944e-12, 6.762388793515361e-08, -0.0006627297804396334, 2.1666411712553812], [-3.0634647703827036e-12, 8.407943128848677e-08, -0.0007965956049746986, 2.545773557437055], [-8.043867327151777e-13, 2.8827477735272883e-08, -0.0003496319743184722, 1.34787667608832],
    #                    [9.472735325782044e-13, -1.8414272142169123e-08, 0.00010639453474275714, -0.16011731471966129], [1.8706793461446896e-12, -4.151166766143467e-08, 0.00029190493266945084, -0.6408077338639665], [-1.3780071545760161e-12, 3.170991526784723e-08, -0.0002355233904377564, 0.5627653239513558]]
    # ADR_y_fit_list =  [[1.0585167511142714e-12, -3.972561095302862e-08, 0.00047854197119031385, -1.806746479722604], [5.712676673528853e-13, -2.7118172653512425e-08, 0.00034731129018336117, -1.322842656375085], [-1.2201306546407504e-12, 2.3629083572706315e-08, -0.00013682268516072916, 0.21158456279065121],
    #                    [-2.0911079335920793e-12, 4.703018551076634e-08, -0.00033904804410673275, 0.7771617214421154], [-2.838537640353266e-12, 6.54908082091063e-08, -0.00048530769637374164, 1.148318135983978], [-3.1271687976010236e-12, 7.140942741912648e-08, -0.0005301049734410775, 1.2753542609892792]] 

    # offsets =  [ -0.2773903893335756 , 0.7159980346947741 , 2.6672716919949306 , 0.8808234960793637,
    #              3, 18,   
    #             #0.5, 18.9, # I got these values with Jamila in Feb 21, but they don´t work 
    #             1.4239020516303178 , 0.003232821107207684 , 1.4757701790022182 , 1.495021090623025 ]
                
    # combined_cube=KOALA_reduce(rss_list, path=path_red, 
    #                            fits_file="combined_cube_.fits",
    #                            rss_clean=True,                 # RSS files are clean
    #                            pixel_size_arcsec=0.7, kernel_size_arcsec=1.1,
    #                            flux_calibration_file=flux_calibration_file,
    #                            #ADR=True,
    #                            plot_tracing_maps=[6400], #[6250,7500,9000],
    #                            size_arcsec=[80,75],
    #                            #box_x=[3,15], box_y=[3,15],
    #                            half_size_for_centroid = 0,   # Using all data for registering
    #                            step_tracing = 20,            # Increase the number of points for tracing
    #                            kernel_tracing = 19,           # Smooth tracing for removing outliers
    #                            g2d=False, 
    #                            adr_index_fit = 3,
                                    
    #                            ADR_x_fit_list = ADR_x_fit_list,
    #                            ADR_y_fit_list = ADR_y_fit_list,
    #                            offsets = offsets,
    #                            reference_rss = 0,
                                    
    #                            trim_cube = True,             # Trimming the cube
    #                            scale_cubes_using_integflux = False, # Not scaling cubes using integrated flux of common region
    #                            plot= True, 
    #                            plot_rss=False, 
    #                            plot_weight=False,
    #                            plot_spectra = False,
    #                            fig_size=12,
    #                            warnings=False, verbose = True)
  

    # # -----------------------------------------------------------------------
    # # -----------------------------------------------------------------------
    # # BLUE DATA (To be done ... )
    # # -----------------------------------------------------------------------
    # # -----------------------------------------------------------------------




    # # -----------------------------------------------------------------------
    # # -----------------------------------------------------------------------
    # # -----------------------------------------------------------------------
    # # -----------------------------------------------------------------------
    # # -----------------------------------------------------------------------
    # # -----------------------------------------------------------------------

    # Truco de Pablo para cambiar algo en header:
    # with fits.open(path_blue+"27feb10031red.fits", "update") as f:
    #     f[0].header["OBJECT"]="He2-10"
    
end= timer()
print("\n> Elapsing time = ",end-start, "s")        