import os
import requests
from io import StringIO

import numpy as np
import matplotlib.pyplot as plt

from astropy import units as u
from astropy.table import Table
from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
from photutils.aperture import SkyCircularAperture, aperture_photometry, ApertureStats

from pykoala.corrections.correction import CorrectionBase
from pykoala.rss import RSS
from pykoala.cubing import Cube
from pykoala.query import PSQuery

def crosscorrelate_im_apertures(ref_aperture_flux, ref_aperture_flux_err,
                                ref_coord, image, wcs,
                                ra_offset_range=[-10, 10],
                                dec_offset_range=[-3, 10],
                                offset_step=0.5, aperture_diameter=1.25):
    """Cross-correlate an image with an input set of apertures.
    
    Description
    -----------
    This method performs a spatial cross-correlation between a list of input aperture fluxes
    and an image.
    First, a grid of aperture position offsets is generated, and every iteration
    will compute the difference between the two sets. 
    """
    print("Cross-correlating image to list of apertures")
    print("Input number of apertures: ", len(ref_aperture_flux))
    # Renormalize the reference aperture
    ref_ap_norm = np.nanmean(ref_aperture_flux)
    ref_flux = ref_aperture_flux / ref_ap_norm
    ref_flux_err = ref_aperture_flux_err / ref_ap_norm
    good_aper = np.isfinite(ref_flux)
    #ref_flux = ref_flux[good_aper]

    ra_offset = np.arange(*ra_offset_range, offset_step)
    dec_offset = np.arange(*dec_offset_range, offset_step)

    results = np.full((4, dec_offset.size, ra_offset.size), fill_value=np.nan)
    results[1:3] = np.meshgrid(dec_offset, ra_offset, indexing='ij')

    
    for i, (ra_offset_arcsec, dec_offset_arcsec) in enumerate(
        zip(results[1].flatten(), results[2].flatten())):
        new_coords = SkyCoord(
            ref_coord.ra + ra_offset_arcsec * u.arcsec,
            ref_coord.dec + dec_offset_arcsec * u.arcsec)
        new_apertures = SkyCircularAperture(
            new_coords, r=aperture_diameter / 2 * u.arcsec)

        table = ApertureStats(image, new_apertures, wcs=wcs, sum_method='exact')

        flux_in_ap = table.mean * np.sqrt(table.center_aper_area.value)
        flux_in_ap_err = table.sum_err
        flux_in_ap_norm = np.nanmean(flux_in_ap)
        flux_in_ap /= flux_in_ap_norm
        flux_in_ap_err /= flux_in_ap_norm

        mask = np.isfinite(flux_in_ap) & good_aper
        n_valid = np.count_nonzero(mask)
        val = np.nansum((flux_in_ap[mask] - ref_flux[mask])**2) / n_valid

        results[:, *np.unravel_index(i, results[0].shape)] = (
            val, ra_offset_arcsec, dec_offset_arcsec,
            ref_ap_norm / flux_in_ap_norm)

    print("Computing the offset solution")
    weights = np.exp(- (results[0] + np.abs(1 - results[3])) / 2)
    weights /= np.nansum(weights)
    # Minimum
    min_pos = np.nanargmax(weights)
    min_pos = np.unravel_index(min_pos, results[0].shape)

    ra_min = results[2][min_pos]
    dec_min = results[1][min_pos]
    ra_mean = np.nansum(results[2] * weights)
    dec_mean = np.nansum(results[1] * weights)
    
    min_coords = SkyCoord(
            ref_coord.ra + ra_min * u.arcsec,
            ref_coord.dec + dec_min * u.arcsec)
    apertures = SkyCircularAperture(
        min_coords, r=aperture_diameter / 2 * u.arcsec)
    table = ApertureStats(image, apertures, wcs=wcs, sum_method='exact')
    min_flux_in_ap = table.mean * np.sqrt(table.center_aper_area.value)

    mean_coords = SkyCoord(
            ref_coord.ra + ra_mean * u.arcsec,
            ref_coord.dec + dec_mean * u.arcsec)
    apertures = SkyCircularAperture(
        mean_coords, r=aperture_diameter / 2 * u.arcsec)
    table = ApertureStats(image, apertures, wcs=wcs, sum_method='exact')
    mean_flux_in_ap = table.mean * np.sqrt(table.center_aper_area.value)


    results = {'offset_min': (ra_min, dec_min), 'offset_mean': (ra_mean, dec_mean),
            'ra_offset': ra_offset, 'dec_offset': dec_offset,
            'results': results, 'weights': weights}
    
    fig, axs = plt.subplots(ncols=3, nrows=1, constrained_layout=True,
                            figsize=(12, 4),
                            sharex=False, sharey=False)
    ax = axs[0]
    mappable = ax.pcolormesh(results['ra_offset'], results['dec_offset'],
                             results['results'][0], cmap='Spectral')
    ax.plot(ra_mean, dec_mean, 'k+', ms=10, label='Weighted')
    ax.plot(ra_min, dec_min, 'k^', label='Minimum')
    ax.set_xlabel("RA offset  (arcsec)")
    ax.set_ylabel("DEC offset  (arcsec)")
    plt.colorbar(mappable, ax=ax, label=r'$(\frac{\hat{f_{ap}}}{<\hat{f_{ap}}>} - \frac{f_{ap}}{<f_{ap}>})^2$',
                 orientation='horizontal', pad=0.2)

    ax = axs[1]
    p95 = np.clip(np.nanpercentile(np.abs(1 - results['results'][-1]), 95),
                  a_min=1, a_max=5)
    mappable = ax.pcolormesh(results['ra_offset'], results['dec_offset'],
                             1 - results['results'][-1], cmap='Spectral',
                             vmin=-p95, vmax=p95)
    ax.plot(ra_mean, dec_mean, 'k+', ms=10, label='Weighted')
    ax.plot(ra_min, dec_min, 'k^', label='Minimum')
    ax.set_xlabel("RA offset (arcsec)")
    plt.colorbar(mappable, ax=ax, label=r'$1 - \frac{f_{ap}}{\hat{f_{ap}}}$',
                 orientation='horizontal', pad=0.2)

    ax = axs[2]
    mappable = ax.pcolormesh(
        results['ra_offset'], results['dec_offset'], results['weights'], cmap='Spectral')
    ax.plot(ra_mean, dec_mean, 'k+', ms=10, label='Weighted')
    ax.plot(ra_min, dec_min, 'k^', label='Minimum')
    ax.legend()
    ax.set_xlabel("RA offset (arcsec)")
    plt.colorbar(mappable, ax=ax, label='Weights',
                 orientation='horizontal', pad=0.2)
    
    vax = ax.inset_axes((1.03, 0, .7, 1))
    vax.plot(results['weights'].sum(axis=1), results['dec_offset'], 'k')
    vax.axhline(dec_min)
    vax.axhline(dec_mean)

    hax = ax.inset_axes((0, 1.03, 1, .7))
    hax.plot(results['ra_offset'], results['weights'].sum(axis=0), 'k')
    hax.axvline(ra_min)
    hax.axvline(ra_mean)

    plt.close(fig)
    results['fig'] = fig

    return results
    
class AncillaryDataCorrection(CorrectionBase):
    name = 'AncillaryData'
    verbose = True

    def __init__(self, data_containers, **kwargs):
        self.data_containers = data_containers
        self.verbose = kwargs.get('verbose', True)

        self.images = kwargs.get("images", dict())

    def get_dc_sky_footprint(self):
        """Get the central sky position of the DataContainers."""
        data_containers_footprint = []
        for dc in self.data_containers:
            if isinstance(dc, Cube):
                footprint = dc.wcs.celestial.calc_footprint()
            elif isinstance(dc, RSS):
                min_ra, max_ra = dc.info['fib_ra'].min(), dc.info['fib_ra'].max()
                min_dec, max_dec = dc.info['fib_dec'].min(), dc.info['fib_dec'].max()
                footprint = np.array(
                    [[max_ra, max_dec],
                     [max_ra, min_dec],
                     [min_ra, max_dec],
                     [min_ra, min_dec]])
            else:
                self.corr_print(f"Unrecognized data container of type: {dc.__class__}")
                continue
            data_containers_footprint.append(footprint)

        self.corr_print("Object footprint: ", data_containers_footprint)
        # Select a rectangle containing all footprints
        max_ra, max_dec = np.nanmax(data_containers_footprint, axis=(0, 1))
        min_ra, min_dec = np.nanmin(data_containers_footprint, axis=(0, 1))
        ra_cen, dec_cen = (max_ra + min_ra) / 2, (max_dec + min_dec) / 2
        ra_width, dec_width = max_ra - min_ra, max_dec - min_dec
        self.corr_print("Combined footprint Fov: ", ra_width * 60, dec_width * 60)
        return (ra_cen, dec_cen), (ra_width, dec_width)
    
    def query_image(self, survey='PS', filters='r', im_extra_size_arcsec=30,
                    im_output_dir='.'):
        """Perform a query of external images that overlap with the DataContainers.
        
        Description
        -----------
        This method performs a query to the database of some photometric survey (e.g. PS)
        and retrieves a set of images that overlap with the IFS data.

        Parameters
        ----------
        - survey: (str, default="PS")
            Name of the external survey/database to perform the query. At present only PS
            queries are available.
        - filters: (str, default='r)
            String containing the filters to be included in the query (e.g. "ugriz").
        - im_extra_size_arcsec: (float, default=30)
            Additional extension of the images in arcseconds with respect to the net FoV
            of the DataContainers.
        - im_output_dir: (str, default='.')
            Path to a directory where the queried images will be stored. Default is current
            working directory.
        Returns
        -------
        """
        self.corr_print("Querying image to external database")
        if survey != 'PS':
            raise NotImplementedError("Currently only PS queries available")

        im_pos, im_fov = self.get_dc_sky_footprint()
        im_pixel_size = int(
            (np.max(im_fov) * 3600 + im_extra_size_arcsec)/ PSQuery.pixelsize_arcsec)
        self.corr_print("Image center sky position (RA, DEC): ", im_pos)
        self.corr_print("Image size (pixels): ", im_pixel_size)
        tab = PSQuery.getimage(*im_pos, size=im_pixel_size, filters=filters)
        if len(tab) == 0:
            return
        # Overide variable
        self.images = {}
        for row in tab:
            print(f"Retrieving cutout: ra={row['ra']}, dec={row['dec']}, filter={row['filter']}")
            sign = np.sign(row['dec'])
            if sign == -1:
                sign_str = 'n'
            else:
                sign_str = ''
            filename = f"ps_query_{row['ra']:.4f}_{sign_str}{np.abs(row['dec']):.4f}_{row['filter']}.fits"
            filename.replace("-", "n")
            output = os.path.join(im_output_dir, filename)
            filename = PSQuery.download_image(row['url'], fname=output)
            if filename is not None:
                intensity, wcs = PSQuery.read_ps_fits(filename)
                self.images[f"PANSTARRS_PS1.{row['filter']}"] = {"intensity": intensity, "wcs":wcs,
                                                                 "pix_size": PSQuery.pixelsize_arcsec}

    def get_dc_aperture_fluxes(self, dc_flux_units=None, aperture_diameter=1.25, sample_every=2):
        """Compute aperture fluxes from the DataContainers"""
        try:
            from pst.observables import Filter
        except:
            raise ImportError("PST package not found")
        if dc_flux_units is None:
            dc_flux_units= 1e-16 * u.erg / u.s / u.cm**2 / u.angstrom
        self.ref_data = {}
        for query_filter in self.images.keys():
            self.ref_data[query_filter] = {'synth_photo': [], 'synth_photo_err': [],
                                           'wcs': [],
                                           'coordinates': [], 'aperture_flux': [],
                                           'aperture_flux_err': [],
                                           'aperture_mask': [],
                                           'figs': []}
            photometric_filter = Filter(filter_name=query_filter)
            for dc in self.data_containers:
                synth_photo, synth_photo_err = self.get_synthetic_photometry(
                    photometric_filter, dc, dc_flux_units)
                self.ref_data[query_filter]['synth_photo'].append(synth_photo)
                self.ref_data[query_filter]['wcs'].append(dc.wcs.celestial.deepcopy())
                self.ref_data[query_filter]['synth_photo_err'].append(synth_photo_err)
                if isinstance(dc, Cube):
                    self.corr_print(
                        "Computing aperture fluxes using Cube synthetic photometry")
                    # Create a grid of apertures equally spaced
                    pix_size_arcsec = np.max(dc.wcs.celestial.wcs.cdelt) * 3600
                    delta_pix = aperture_diameter / pix_size_arcsec * sample_every
                    self.corr_print(
                        f"Creating a grid of circular aperture (rad={aperture_diameter / 2 / pix_size_arcsec:.2f} px) every {delta_pix:.1f} pixels")
                    rows = np.arange(0, synth_photo.shape[0], delta_pix)
                    columns = np.arange(0, synth_photo.shape[1], delta_pix)
                    yy, xx = np.meshgrid(rows, columns)
                    coordinates = dc.wcs.celestial.pixel_to_world(xx.flatten(), yy.flatten())
                    apertures = SkyCircularAperture(
                        coordinates, r=aperture_diameter / 2 * u.arcsec)
                    self.corr_print(f"Total number of apertures: {len(apertures)}")
                    reference_table = ApertureStats(data=synth_photo, error=synth_photo_err,
                    aperture=apertures, wcs=dc.wcs.celestial, sum_method='exact')
                    # Compute the total flux in the aperture using the mean value
                    flux_in_ap = reference_table.mean * np.sqrt(
                        reference_table.center_aper_area.value)
                    # Compute standard error from the std
                    flux_in_ap_err = reference_table.sum_err
                elif isinstance(dc, RSS):
                    self.corr_print("Using RSS synthetic photometry as apertures")
                    coordinates = SkyCoord(dc.info['fib_ra'], dc.info['fib_dec'])
                    flux_in_ap, flux_in_ap_err = synth_photo, synth_photo_err
                fig = self.make_plot_apertures(
                    dc, synth_photo, synth_photo_err, coordinates, flux_in_ap, flux_in_ap_err)
                self.ref_data[query_filter]['figs'].append(fig)
                self.ref_data[query_filter]['coordinates'].append(coordinates)
                self.ref_data[query_filter]['aperture_flux'].append(flux_in_ap)
                self.ref_data[query_filter]['aperture_flux_err'].append(flux_in_ap_err)
                self.ref_data[query_filter]['aperture_mask'].append(
                    np.isfinite(flux_in_ap) & np.isfinite(flux_in_ap_err))
        return self.ref_data
    
    def get_synthetic_photometry(self, filter, dc, dc_flux_units):
        """Compute synthetic photometry using a DataContainer."""
        filter.interpolate(dc.wavelength)
        if isinstance(dc, Cube):
            rss_intensity = dc.intensity.reshape(
                    dc.intensity.shape[0], dc.intensity.shape[1] * dc.intensity.shape[2])
            rss_var = dc.variance.reshape(rss_intensity.shape)
            synth_photo = np.full(rss_intensity.shape[1], fill_value=np.nan)
            synth_photo_err = np.full(rss_intensity.shape[1], fill_value=np.nan)
            for ith, (intensity, var) in enumerate(zip(rss_intensity.T, rss_var.T)):
                mask = np.isfinite(intensity) & np.isfinite(var)
                if not mask.any():
                    continue
                f_nu, f_nu_err = filter.get_fnu(intensity * dc_flux_units,
                                                            var**0.5 * dc_flux_units)
                synth_photo[ith] = f_nu.value
                synth_photo_err[ith] = f_nu_err.value
            synth_photo = synth_photo.reshape(dc.intensity.shape[1:])
            synth_photo_err = synth_photo_err.reshape(dc.intensity.shape[1:])
        elif isinstance(dc, RSS):
            synth_photo = np.full(dc.intensity.shape[1], fill_value=np.nan)
            synth_photo_err = np.full(dc.intensity.shape[1], fill_value=np.nan)
            for ith, (intensity, var) in enumerate(zip(dc.intensity.T, dc.variance.T)):
                mask = np.isfinite(intensity) & np.isfinite(var)
                if not mask.any():
                    continue
                f_nu, f_nu_err = filter.get_fnu(intensity * dc_flux_units,
                                                            var**0.5 * dc_flux_units)
                synth_photo[ith] = f_nu.value
                synth_photo_err[ith] = f_nu_err.value

        return synth_photo, synth_photo_err

    def make_plot_apertures(self, dc, synth_phot, synth_phot_err, ap_coords, ap_flux, ap_flux_err):
        if isinstance(dc, Cube):
            fig, axs = plt.subplots(ncols=2, nrows=2, sharex=True, sharey=True,
                                    subplot_kw={'projection': dc.wcs.celestial},
                                    constrained_layout=True)
            ax = axs[0, 0]
            mappable = ax.imshow(-2.5 * np.log10(synth_phot / 3631), vmin=16, vmax=23,
                                 interpolation='none')
            plt.colorbar(mappable, ax=ax, label='SB (mag/pix)')
            ax = axs[0, 1]
            mappable = ax.imshow(synth_phot / synth_phot_err, vmin=0, vmax=10, cmap='jet',
                                 interpolation='none')
            plt.colorbar(mappable, ax=ax, label='Flux SNR')
            ax = axs[1, 0]            
            mappable = ax.scatter(ap_coords.ra, ap_coords.dec,
            marker='o', transform=ax.get_transform('world'),
            c= -2.5 * np.log10(ap_flux / 3631), vmin=16, vmax=23)
            plt.colorbar(mappable, ax=ax, label='SB (mag/aperture)')
            ax = axs[1, 1]            
            mappable = ax.scatter(ap_coords.ra, ap_coords.dec,
            marker='o', transform=ax.get_transform('world'),
            c= ap_flux /ap_flux_err, vmin=0, vmax=10)
            plt.colorbar(mappable, ax=ax, label='Aper flux SNR')
            for ax in axs.flatten():
                ax.coords.grid(True, color='orange', ls='solid')
                ax.coords[0].set_format_unit('deg')
            plt.close(fig)
        return fig
    
    def make_plot_astrometry_offset(self, ref_image, ref_wcs, image, results):
        """..."""        
        fig = plt.figure(figsize=(10, 4))
        ax = fig.add_subplot(121, title='Original', projection=image['wcs'])
        ax.coords.grid(True, color='orange', ls='solid')
        ax.coords[0].set_format_unit('deg')
        mappable = ax.imshow(
            -2.5 * np.log10(image['intensity'] / 3631 / image['pix_size']**2))
        plt.colorbar(mappable, ax=ax, label=r"$\rm \log_{10}(F_\nu / Jy / arcsec^2)$")

        ax.contour(np.log10(ref_image), transform=ax.get_transform(ref_wcs),
                   levels=10)
        
        correc_wcs = ref_wcs.deepcopy()
        if "RA" in correc_wcs.wcs.ctype[0]:
            correc_wcs.wcs.crval[0] = correc_wcs.wcs.crval[0] + results['offset_min'][0] / 3600
            correc_wcs.wcs.crval[1] = correc_wcs.wcs.crval[1] + results['offset_min'][1] / 3600
        else:
            print("Nope")
            correc_wcs.wcs.crval[0] = correc_wcs.wcs.crval[0] + results['offset_min'][1] / 3600
            correc_wcs.wcs.crval[1] = correc_wcs.wcs.crval[1] + results['offset_min'][0] / 3600

        ax = fig.add_subplot(122, title='Corrected', projection=image['wcs'])
        ax.coords.grid(True, color='orange', ls='solid')
        ax.coords[0].set_format_unit('deg')
        mappable = ax.imshow(
            -2.5 * np.log10(image['intensity'] / 3631 / image['pix_size']**2))
        plt.colorbar(mappable, ax=ax, label=r"$\rm \log_{10}(F_\nu / Jy / arcsec^2)$")

        ax.contour(np.log10(ref_image), transform=ax.get_transform(correc_wcs),
                   levels=10)
        plt.close(fig)
        return fig

    def get_astrometry_offset(self):
        """Compute astrometric offsets using apertures.
        
        Description
        -----------
        Compute the astrometric offsets that match the synthetic
        aperture photometry to the external image.
        """
        self.corr_print("Computing astrometric offsets")
        for ith, dc in enumerate(self.data_containers):
            for filter in self.images.keys():
                mask = self.ref_data[filter]['aperture_mask'][ith]
                results = crosscorrelate_im_apertures(
                    self.ref_data[filter]['aperture_flux'][ith][mask],
                    self.ref_data[filter]['aperture_flux_err'][ith][mask],
                    self.ref_data[filter]['coordinates'][ith][mask],
                    self.images[filter]['intensity'],
                    self.images[filter]['wcs'])
                fig = self.make_plot_astrometry_offset(
                    self.ref_data[filter]['synth_photo'][ith],
                    self.ref_data[filter]['wcs'][ith],
                    self.images[filter], results)
                results['offset_fig'] = fig
        return results

    def apply():
        pass