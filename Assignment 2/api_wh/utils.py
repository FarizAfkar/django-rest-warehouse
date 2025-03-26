from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
import xhtml2pdf.pisa as pisa


class Render:
    @staticmethod
    def render(path: str, params: dict):
        """
        Render an HTML template to a PDF response.

        :param template_src: Path to the HTML template.
        :param context_dict: Context data to render in the template.
        :return: HttpResponse with PDF.
        """
        template = get_template(path)
        html = template.render(params)
        response = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-8')), response)
        if not pdf.err:
            return HttpResponse(response.getvalue(), content_type = 'application/pdf')
        else:
            return HttpResponse('Error Rendering PDF', status = 400)
