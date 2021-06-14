import csv
import xml.etree.ElementTree as ET
from cStringIO import StringIO
from DateTime import DateTime
from bika.lims import api
from bika.lims.catalog import CATALOG_ANALYSIS_REQUEST_LISTING
from bika.lims.exportimport.instruments import IInstrumentAutoImportInterface
from bika.lims.exportimport.instruments import IInstrumentExportInterface
from bika.lims.exportimport.instruments import IInstrumentImportInterface
from bika.lims.exportimport.instruments.utils import \
    get_instrument_import_ar_allowed_states
from bika.lims.exportimport.instruments.utils import \
    get_instrument_import_override
from bika.lims.exportimport.instruments.resultsimport import AnalysisResultsImporter
from bika.lims.exportimport.instruments.resultsimport import \
    InstrumentCSVResultsFileParser
from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import getUtility
from zope.interface import implements


class bciimport(object):
    implements(IInstrumentImportInterface)
    title="Jonathans Groovey_BCI_Importer"

    def __init__(self, context):
        self.context = context
        self.request = None

    def Import(self, context, request):
        """ Read Dimensional-CSV analysis results
        """

        infile = request.form['instrument_results_file']
        fileformat = request.form.get(
            'instrument_results_file_format', 'xml')
        artoapply = request.form['artoapply']
        override = request.form['results_override']
        instrument = request.form.get('instrument', None)
        errors = []
        logs = []
        warns = []
        parser = None
        if not hasattr(infile, 'filename'):
            errors.append(_("No file selected"))
        parser = BCIXMLParser(infile)
        status = get_instrument_import_ar_allowed_states(artoapply)
        over = get_instrument_import_override(override)
        importer = BCI_Importer(
            parser=parser,
            context=context,
            allowed_ar_states=status,
            allowed_analysis_states=None,
            override=over,
            instrument_uid=instrument,
            form=form)
        tbex = ''
        try:
            importer.process()
        except Exception as e:
            tbex = traceback.format_exc()
        errors = importer.errors
        logs = importer.logs
        warns = importer.warns
        if tbex:
            errors.append(tbex)

        results = {'errors': errors, 'log': logs, 'warns': warns}

        return json.dumps(results)


class BCI_Importer(AnalysisResultsImporter):
    def __init__(self, parser, context, override,
                 allowed_ar_states=None, allowed_analysis_states=None,
                 instrument_uid='', form=None):
        AnalysisResultsImporter.__init__(self, parser, context,
                                         override, allowed_ar_states,
                                         allowed_analysis_states,
                                         instrument_uid)
