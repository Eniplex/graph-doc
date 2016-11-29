import json

import re

import configparser
import datetime
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
import io

from reportlab.pdfgen import canvas
from reportlab.platypus import BaseDocTemplate
from reportlab.platypus import Frame
from reportlab.platypus import PageBreak
from reportlab.platypus import PageTemplate
from reportlab.platypus import Paragraph
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Spacer
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.colors import (
    black,
    purple,
    white,
    yellow,
    red
)


from careerjapan.gql.schema import SCHEMA_ADMIN
from careerjapan.gql.schema import SCHEMA_JOBSEEKER


class IntroSpectDocTemplate(BaseDocTemplate):
    def __init__(self, filename, **kw):
        self.allowSplitting = 0
        apply(BaseDocTemplate.__init__, (self, filename), kw)
        template = PageTemplate('normal', [Frame(0.4*inch, 0.2*inch, 8.5*inch, 11*inch, id='F1')])
        self.addPageTemplates(template)

    def afterFlowable(self, flowable):
        "Register TOC Entries."
        if flowable.__class__.__name__== 'Paragraph':
            text = flowable.getPlainText()
            style = flowable.style.name

            if style == 'Heading4':
                toc_el = [3, text, self.page]
                toc_bm = getattr(flowable, '_bookmarkName', None)
                if toc_bm:
                    toc_el.append(toc_bm)
                self.notify('TOCEntry', tuple(toc_el))

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.setFont("Helvetica", 7)
        self.drawRightString(200 * mm, 20 * mm,
                             "Page %d of %d" % (self._pageNumber, page_count))

#this function makes our headings
def doHeading(text,sty):
    from hashlib import sha1
    bn=sha1(text+sty.name).hexdigest()
    h=Paragraph(text+'<a name="%s"/>' % bn,sty)
    h._bookmarkName=bn
    return h

centred = ParagraphStyle(
        name = 'Normal', #'centred',
        fondSize = 10,
        leading = 12,
        # allignment = 1,
        spaceAfter = 4

    )

h4 = ParagraphStyle(
    name = 'Heading4',
    fontSize = 15,
    leading = 12,
    spaceAfter = 4
)

t1 = ParagraphStyle(
    name = 'Normal',
    fontSize = 10,
    leading = 12,
    leftIndent=20
)

t2 = ParagraphStyle(
    name = 'Normal',
    fontSize = 10,
    leading = 12,
    leftIndent=40
)

t3 = ParagraphStyle(
    name = 'Normal',
    fontSize = 10,
    leading = 12,
    leftIndent=60
)

t4 = ParagraphStyle(
    name = 'Normal',
    fontSize = 10,
    leading = 12,
    leftIndent=80
)

toc = TableOfContents()
toc.levelStyles = [
    # ParagraphStyle(fontName = 'Times-Bold', fontSize = 10, name = 'TOCHeading1', leftIndent=20, firstLineIndent=-20, spaceBefore=10, leading=12),
    # ParagraphStyle(fontSize = 10, name = 'TOCHeading2', leftIndent=20, firstLineIndent=-20, spaceBefore=10, leading=12)
    ParagraphStyle(fontName = 'Times-Bold', fontSize = 10, name = 'TOCHeading1', leftIndent=20, firstLineIndent=-80, spaceBefore=10, leading=12),
    ParagraphStyle(fontSize = 10, name = 'TOCHeading2', leftIndent=20, firstLineIndent=-80, spaceBefore=10, leading=12)
]

class Mutation(object):
    def __init__(self, name, desc, arg_desc, input, payload):
        self.name = name
        self.desc = desc
        self.arg_desc = arg_desc
        self.input = input
        self.payload = payload

def create_front_page():
    pargraph = []

    config = configparser.ConfigParser()
    config.read('./instance/introspect_doc.ini')
    title = config['title']['keys']
    project = config['project']['keys']
    major_ver = config['version']['major']
    minor_ver = config['version']['minor']
    company = config['company']['keys']
    owner = config['owner']['keys']
    date = datetime.datetime.now().date()

    pargraph.append(Paragraph('Eniplex Confidential', ParagraphStyle('Normal', leftIndent=450, textColor=red)))
    for i in range(0, 20):
        pargraph.append(Spacer(5,12))
    pargraph.append(Paragraph('<b>%s</b>' % title, ParagraphStyle('Heading1', fontSize=24)))
    for i in range(0, 5):
        pargraph.append(Spacer(5,12))
    pargraph.append(Paragraph('<b>for</b>' , ParagraphStyle('Heading1', fontSize=15)))
    for i in range(0, 4):
        pargraph.append(Spacer(5,12))
    pargraph.append(Paragraph('<b>%s V%s</b>' % (project, major_ver), ParagraphStyle('Heading1', fontSize=24)))

    for i in range(0, 20):
        pargraph.append(Spacer(5,12))
    pargraph.append(Paragraph('<b>Version %s.%s</b>' % (major_ver, minor_ver), ParagraphStyle('Heading1', fontSize=15)))

    for i in range(0, 2):
        pargraph.append(Spacer(5,12))
    pargraph.append(Paragraph('<b>Prepared by %s</b>' % (company), ParagraphStyle('Heading1', fontSize=15)))
    pargraph.append(Spacer(5, 12))
    pargraph.append(Paragraph('<b>For %s</b>' % (owner), ParagraphStyle('Heading1', fontSize=15)))
    for i in range(0, 2):
        pargraph.append(Spacer(5,12))
    pargraph.append(Paragraph('<b>Prepared on %s</b>' % (date), ParagraphStyle('Heading1', fontSize=15)))
    pargraph.append(PageBreak())

    # doc = IntroSpectDocTemplate('front_page.pdf')
    # doc.multiBuild(pargraph)
    return  pargraph

def create_toc_page():
    paragraph = []
    paragraph.append(Spacer(1, 12))
    paragraph.append(Paragraph('<b>Table of contents</b>', ParagraphStyle('normal')))
    paragraph.append(toc)
    paragraph.append(PageBreak())

    return paragraph

def introspect_schema_admin():
    paragraphs = []
    paragraphs2 = []
    paragraph3 = []
    # paragraphs.append(toc)

    # paragraphs.append(Spacer(1,12))
    # paragraphs.append(Paragraph('<b>Table of contents</b>', ParagraphStyle('normal')))
    # paragraphs.append(toc)
    # paragraphs.append(PageBreak())
    # paragraphs.append(doHeading('<b>Quary admin</b>', h4))

    introspect_dict = SCHEMA_ADMIN.introspect()
    fp = open("introspect_schme_admin.json", "w")
    json.dump(introspect_dict, fp)
    fp.close()

    payload_list = []
    input_objects = []
    interface_node_list = []
    add_header = True
    input_object_header = True
    interface_node_header = True
    input_object_counter = 1
    field_counter = 1

    payload_counter = 1
    for key in introspect_dict:
        if key == "__schema":
            for value  in introspect_dict[key]:
                if value == 'types':
                    list = introspect_dict[key][value]
                    node_count = 1
                    for list_value in list:

                        for list_key in list_value:
                            if list_key == 'name' and list_value[list_key] == 'AdminMutationRoot':
                                paragraphs.append(Spacer(1, 12))
                                # paragraphs.append(doHeading('<b>Mutations of Admin Entity</b>', h4))
                                field_value = list_value['fields']
                                count = 1
                                for key_field_value in field_value:
                                    # paragraphs.append(Paragraph('<b>%d.</b> %s' % (count, key_field_value['name'] ), ParagraphStyle('Normal')))
                                    # Add the details of mutation in the mutation class
                                    paragraphs2.append(Mutation(key_field_value['name'],key_field_value['description'], (key_field_value['args'][0].values()[1]), (key_field_value['args'][0].values()[2].values()[2].values()[1]),key_field_value['type'].values()[1]))
                                    # if (key_field_value['description']):
                                    #     paragraphs.append(Paragraph('description : %s' % (key_field_value['description']), ParagraphStyle('Normal')))
                                    # paragraphs.append(Paragraph('Mutation input name: ', t1))
                                    # paragraphs.append(Spacer(12,1))
                                    # paragraphs.append(Paragraph('name: %s' % (key_field_value['args'][0].values()[0]),t1))
                                    # paragraphs.append(Paragraph('%s' % (key_field_value['args'][0].values()[2].values()[2].values()[1]),t2))
                                    # if (key_field_value['args'][0].values()[1]):
                                    #     paragraphs.append(Paragraph('%s' % (key_field_value['args'][0].values()[1]),t2))

                                    input_objects.append(key_field_value['args'][0].values()[2].values()[2].values()[1])
                                    # paragraphs.append(Paragraph('ofType: %s' % (key_field_value['args'][0].values()[2].values()[2].values()[2]),t3))
                                    # paragraphs.append(Paragraph('defaultValue: %s' % (key_field_value['args'][0].values()[3]), t1))
                                    # paragraphs.append(Paragraph('Mutation payload name: ', t1))
                                    # paragraphs.append(Paragraph('%s' % (key_field_value['type'].values()[1]), t2))
                                    payload_list.append(key_field_value['type'].values()[1])
                                    # paragraphs.append(Spacer(1,12))
                                    # count +=1

                            # if list_key == 'name' and list_value[list_key] in input_objects:
                            if list_key == 'kind' and list_value[list_key] == "INPUT_OBJECT":

                                # if list_value['name'] in input_objects:
                                #     paragraphs.append(Paragraph('Fields required in mutation input: ', t2))
                                # if input_object_header == True:
                                #     paragraphs.append(doHeading('<b>Input object relations:</b>', h4))
                                #     input_object_header = False
                                # paragraphs.append(Paragraph('<b>%d</b>name: %s' % (input_object_counter, list_value[list_key]), ParagraphStyle('Normal')))
                                # paragraphs.append(Paragraph('kind: %s' % list_value['kind'], ParagraphStyle('Normal')))
                                input_field_values = list_value['inputFields']


                                input_field_cnt = 1
                                paragraphs.append(Paragraph('<b>-</b> %s' % list_value['name'], t2))
                                for input_field_val_el in input_field_values:
                                    if(input_field_val_el['type'].values()[1]):
                                        paragraphs.append(Paragraph('<b>*</b> %s (%s)' % ( input_field_val_el['name'], input_field_val_el['type'].values()[1]), t3))
                                    else:
                                        if (input_field_val_el['type'].values()[2]['name']):
                                            paragraphs.append(Paragraph('<b>*</b> %s (%s)' % (input_field_val_el['name'], input_field_val_el['type'].values()[2]['name']), t3))
                                        else:
                                            paragraphs.append(Paragraph('<b>*</b> %s' % (input_field_val_el['name']),t3))
                                    field_counter +=1
                                    input_field_cnt+=1

                                paragraphs.append(Spacer(1,12))


                                input_object_counter +=1

                            if list_key == 'name' and list_value[list_key] in payload_list:
                                # print list_value['name']
                                if add_header == True:
                                    paragraphs.append(doHeading('<b>Mutations of Admin Entity</b>', h4))
                                    add_header = False
                                # paragraphs.append(Paragraph('<b>%d.</b>kind: %s' %(payload_counter, list_value['kind']), ParagraphStyle('Normal')))

                                # Add paragrah3 with paragraps at here and clear paragraph3.
                                paragraphs = paragraphs + paragraph3
                                del paragraph3[:]

                                for mutation_el in paragraphs2:
                                    if mutation_el.payload == list_value[list_key]:
                                        if payload_counter != 1:
                                            paragraphs.append(Spacer(1, 12))
                                        paragraphs.append(Paragraph('<b>%d.</b> %s' % (payload_counter, mutation_el.name), ParagraphStyle('Normal')))
                                        if (mutation_el.desc):
                                            paragraphs.append(
                                                Paragraph('Description : %s' % (mutation_el.desc), t1))
                                            paragraphs.append(Spacer(1, 12))

                                        paragraphs.append(Paragraph('Mutation inputs name: ', t1))
                                        # paragraphs.append(Spacer(1, 12))
                                        # paragraphs.append(Paragraph('%s' % (mutation_el.input),t2))

                                        # from here the data is appended to paragraph3 to adjust the content in the paragraph.
                                        if (mutation_el.arg_desc):
                                            paragraph3.append(Paragraph('Args description: %s' % (mutation_el.arg_desc),t2))
                                            paragraph3.append(Spacer(1, 12))
                                        paragraph3.append(Paragraph('Mutation payload name: ', t1))
                                        paragraph3.append(Paragraph('%s' % (mutation_el.payload), t2))

                                        fields_value_list = list_value['fields']
                                        # paragraph3.append(Paragraph('Fields required:', t2))
                                        fields_cnt = 1
                                        for fields_value_list_el in fields_value_list:
                                            if (fields_value_list_el['type'].values()[1]):
                                                paragraph3.append(
                                                    Paragraph('<b>-</b> %s (%s)' % (fields_value_list_el['name'], fields_value_list_el['type'].values()[1]), t3))
                                            else:
                                                paragraph3.append(
                                                    Paragraph('<b>-</b> %s' % (fields_value_list_el['name']), t3))
                                            fields_cnt += 1
                                        paragraph3.append(Spacer(1, 12))
                                        break


                                paragraph3.append(Paragraph('Mutation description:', t1))
                                paragraph3.append(Paragraph('Name: ', t2))
                                paragraph3.append(Paragraph('%s' % (list_value['name']), t3))

                                payload_detail = list_value['description']
                                payload_counter += 1

                                if (payload_detail):
                                    zero_point = payload_detail.find('EventRegistrationStatus')


                                    first_point = payload_detail.find("Description")

                                    second_point = payload_detail.find("Feature")
                                    third_point = payload_detail.find("Sample Request")
                                    if third_point == -1:
                                        third_point = payload_detail.find("Example Request")

                                    fourth_point = payload_detail.find('Sample Input')
                                    if fourth_point == -1:
                                        fourth_point = payload_detail.find('Example Input')
                                        if fourth_point == -1:
                                            fourth_point = payload_detail.find('Variable Input')

                                    fifth_point = payload_detail.find('File Inputs')
                                    sixth_point = payload_detail.find('Error Codes')
                                    event_reg_status = ''

                                    if zero_point != -1:
                                        detail = payload_detail[0:zero_point]
                                        if first_point != -1:
                                            event_reg_status = payload_detail[zero_point+ len('EventRegistrationStatus:'):first_point]
                                        else:
                                            detail = ''

                                    else:
                                        if first_point != -1:
                                            detail = payload_detail[0:first_point]
                                        else:
                                            detail = ''

                                    if second_point != -1:
                                        description = payload_detail[first_point + len("Description:\n"):second_point]
                                        feature = payload_detail[second_point + len("Feature:"):third_point]
                                    else:
                                        feature = ''
                                        description = payload_detail[first_point + len("Description:\n"):third_point]


                                    sample_request = payload_detail[third_point+ len('Sample Request:\n'):fourth_point]

                                    if fifth_point != -1:
                                        varrible_input = payload_detail[fourth_point + len('Sample Input :  \n'): fifth_point]
                                        if sixth_point != -1:
                                            file_input = payload_detail[fifth_point+ len('File Inputs:'): sixth_point]
                                        else:
                                            file_input = payload_detail[fifth_point + len('File Inputs:'): len(payload_detail) ]
                                    else:
                                        if sixth_point != -1:
                                            varrible_input = payload_detail[fourth_point + len('Sample Input:\n'): sixth_point]
                                        else:
                                            varrible_input = payload_detail[fourth_point + len('Sample Input:\n'): len(payload_detail)]
                                        file_input =''

                                    if sixth_point != -1:
                                        error_codes = payload_detail[sixth_point + len('Error Codes:\n'): len(payload_detail)]
                                    else:
                                        error_codes = ''

                                    event_reg_sta_list = event_reg_status.splitlines()
                                    file_input_list = file_input.splitlines()
                                    error_codes_list = error_codes.splitlines()

                                    sample_request_list = sample_request.splitlines()
                                    sample_input_list = varrible_input.splitlines()

                                    # paragraphs.append(Paragraph('description:', ParagraphStyle('Normal')))
                                    paragraph3.append(Paragraph('Detail:', t2))
                                    paragraph3.append(Paragraph('%s' % detail, t3))
                                    if (event_reg_sta_list):
                                        paragraph3.append(Paragraph('Event register status:', t2))
                                        for event_reg_sta_el in event_reg_sta_list:
                                            paragraph3.append(Paragraph('%s' % event_reg_sta_el, t3))
                                    if (description):
                                        paragraph3.append(Paragraph('Description:', t2))
                                        paragraph3.append(Paragraph('%s' % (description), t3))

                                    if (feature):
                                        paragraph3.append(Paragraph('Feature:',t2))
                                        paragraph3.append(Paragraph('%s' % feature, t3))

                                    # #

                                    paragraph3.append(Paragraph('Sample Request: ', t2))
                                    left_indent = 60
                                    paragraph3.append(Paragraph('<b>\"</b>',ParagraphStyle('Normal', leftIndent = 60) ))
                                    for sam_req_el in sample_request_list:
                                        if sam_req_el.find("{") != -1:
                                            paragraph3.append(Paragraph('%s' % sam_req_el, ParagraphStyle('Normal', leftIndent = left_indent)))
                                            left_indent += 10
                                        elif sam_req_el.find("}") != -1:
                                            left_indent -= 10
                                            paragraph3.append(Paragraph('%s' % sam_req_el, ParagraphStyle('Normal', leftIndent = left_indent)))
                                        else:
                                            paragraph3.append(Paragraph('%s' % sam_req_el, ParagraphStyle('Normal', leftIndent=left_indent)))
                                    paragraph3.append(Paragraph('<b>\"</b>',ParagraphStyle('Normal', leftIndent = 60) ))

                                    # paragraphs.append(Paragraph('%s' % sample_request, t2))
                                    paragraph3.append(Paragraph('Sample Input: ', t2))
                                    left_indent = 60
                                    paragraph3.append(Paragraph('<b>\"</b>',ParagraphStyle('Normal', leftIndent = 60) ))
                                    for sam_in_el in sample_input_list:
                                        if sam_in_el.find("{") != -1:
                                            paragraph3.append(Paragraph('%s' % sam_in_el, ParagraphStyle('Normal', leftIndent = left_indent)))
                                            left_indent += 10
                                        elif sam_in_el.find("}") != -1:
                                            left_indent -= 10
                                            paragraph3.append(Paragraph('%s' % sam_in_el, ParagraphStyle('Normal', leftIndent = left_indent)))
                                        else:
                                            paragraph3.append(Paragraph('%s' % sam_in_el, ParagraphStyle('Normal', leftIndent= left_indent)))

                                    paragraph3.append(Paragraph('<b>\"</b>',ParagraphStyle('Normal', leftIndent = 60) ))
                                    # paragraphs.append(Paragraph('%s' % varrible_input, t2))
                                    if (file_input_list):
                                        paragraph3.append(Paragraph('File Inputs: ', t2))
                                        for file_in_el in file_input_list:
                                            if (not re.match(r"[ \t]*$", file_in_el)):
                                                paragraph3.append(Paragraph('<b>-</b> %s' %file_in_el, t3))
                                    if (error_codes_list):
                                        paragraph3.append(Paragraph('Error Codes:',t2))
                                        for err_el in error_codes_list:
                                            if (not re.match(r"[ \t]*$", err_el)):
                                                paragraph3.append(Paragraph('<b>-</b> %s' % err_el, t3))



                                        # print fields_value_list_el['name']

                                # paragraphs.append(Spacer(1, 12))



                            if list_key == 'name' and list_value[list_key] == 'Query_Admin':
                                field_value = list_value['fields']
                                count = 1
                                paragraphs.append(doHeading('<b>Admin quaries:</b>', h4))
                                for key_field_value in field_value:
                                    paragraphs.append(Paragraph('<b>%d.</b> Name : %s' % (count, key_field_value['name']), ParagraphStyle('Normal') ))
                                    paragraphs.append(Paragraph('description : %s' % (key_field_value['description']), ParagraphStyle('Normal')))
                                    # paragraphs.append(Paragraph('args : ', ParagraphStyle('Normal')))
                                    # args_list = key_field_value['args']
                                    # for args_list_el in args_list:
                                    #     paragraphs.append(Paragraph('name: %s' % args_list_el['name'], t1))
                                    #     paragraphs.append(Paragraph('description: %s' % args_list_el['description'], t1))
                                    #
                                    # paragraphs.append(Paragraph('Type : ', ParagraphStyle('Normal')))
                                    # paragraphs.append(Paragraph('name: %s' % key_field_value['type'].values()[1], t1))
                                    # paragraphs.append(Paragraph('kind: %s' % key_field_value['type'].values()[0], t1))


                                    # paragraphs.append(Paragraph('Is Deprecated : %s' % (key_field_value['isDeprecated']),ParagraphStyle('Normal')))
                                    # paragraphs.append(Paragraph('Deprecation Reason : %s' % (key_field_value['deprecationReason']),ParagraphStyle('Normal')))
                                    paragraphs.append(Spacer(1, 12))
                                    count +=1


                            if list_value[list_key] == 'INTERFACE' and list_value['name'] == 'Node':
                                paragraphs.append(doHeading('<b>Interface nodes (Admin):</b>', h4))
                                paragraphs.append(Paragraph('Name: %s' % list_value['name'], ParagraphStyle('Normal')))
                                paragraphs.append(Paragraph('Kind: %s' % list_value['kind'], ParagraphStyle('Normal')))
                                paragraphs.append(Paragraph('Description: %s' % list_value['description'], ParagraphStyle('Normal')))
                                paragraphs.append(Paragraph('Fields:', ParagraphStyle('Normal')))

                                interface_field_list = list_value['fields']
                                for interface_field_list_el in interface_field_list:
                                    # paragraphs.append(Paragraph('name: %s' % interface_field_list_el['name'], t1))
                                    paragraphs.append(Paragraph('description: %s' % interface_field_list_el['description'], t1))

                                # paragraphs.append(Paragraph('Input fields: %s' % list_value['inputFields'], ParagraphStyle('Normal')))
                                # paragraphs.append(Paragraph('Intrefaces: %s' % list_value['interfaces'], ParagraphStyle('Normal')))
                                # paragraphs.append(Paragraph('Enum values: %s' % list_value['enumValues'], ParagraphStyle('Normal')))
                                paragraphs.append(Paragraph('Possible interface types: ', ParagraphStyle('Normal')))


                                count = 1;
                                possible_types = list_value['possibleTypes']
                                for value_possible_type in possible_types:
                                    paragraphs.append(Paragraph('<b>-</b> %s' % ( value_possible_type['name']), t1 ))
                                    interface_node_list.append(value_possible_type['name'])
                                    count += 1

                            if list_key == 'name' and list_value[list_key] in interface_node_list:
                                if interface_node_header:
                                    paragraphs.append(Spacer(1, 12))
                                    paragraphs.append(doHeading('<b>Available interface nodes (Admin). </b>', h4))
                                    interface_node_header = False

                                paragraphs.append(Paragraph('<b>-</b> %s' % ( list_value['name']), t1))
                                if (list_value['description']):
                                    paragraphs.append(Paragraph('<b>description: </b> %s' % (list_value['description']), t2))

                                list_node_fields = list_value['fields']
                                # if (list_node_fields):
                                #     paragraphs.append(Paragraph('Fields:', t2))
                                for list_node_fields_el in list_node_fields:
                                    if (list_node_fields_el.values()[3]['name']):
                                        paragraphs.append(Paragraph('<b>*</b> %s (%s)' % (list_node_fields_el.values()[0], list_node_fields_el.values()[3]['name']), t3))
                                        if(list_node_fields_el.values()[1]):
                                            paragraphs.append(Paragraph('description: %s' % (list_node_fields_el.values()[1]), t4))
                                    else:
                                        if (list_node_fields_el.values()[3]['ofType'].values()[1]):
                                            paragraphs.append(Paragraph('<b>*</b> %s (%s)' % (list_node_fields_el.values()[0], list_node_fields_el.values()[3]['ofType'].values()[1]), t3))
                                        else:
                                            paragraphs.append(Paragraph('<b>*</b> %s' % (list_node_fields_el.values()[0]), t3))
                                        if (list_node_fields_el.values()[1]):
                                            paragraphs.append(Paragraph('description: %s' % (list_node_fields_el.values()[1]),t4))
                                # if (list_value['description']):
                                #     paragraphs.append(Paragraph('description: %s' % list_value['description'], ParagraphStyle('Normal')))
                                paragraphs.append(Spacer(1,12))
                                node_count +=1

    #Add the remaining content in paragraph3
    paragraphs = paragraphs + paragraph3

    # paragraphs.append(Paragraph("This is first content", ParagraphStyle('Normal')))
    # paragraphs.append(Paragraph('Interface nodes', h4))
    # paragraphs.append(Paragraph('Admin mutation root', h4))
    # print payload_list
    # print input_objects
    # paragraphs.append(doHeading('<b>Input object relations:</b>', h4))
    paragraphs.append(PageBreak())

    # doc = IntroSpectDocTemplate('server_admin.pdf')
    # doc.multiBuild(paragraphs, canvasmaker=NumberedCanvas)
    return paragraphs

def introspect_schema_jobseeker():
    paragraphs = []
    paragraphs2 = []
    paragraph3 = []
    # paragraphs.append(toc)
    #
    # paragraphs.append(Paragraph('<b>Table of contents</b>', centred))
    # paragraphs.append(PageBreak())
    # # paragraphs.append(doHeading('<b>Quary admin</b>', h4))

    introspect_dict = SCHEMA_JOBSEEKER.introspect()
    fp = open("introspect_schme_jobseeker.json", "w")
    json.dump(introspect_dict, fp)
    fp.close()

    payload_list = []
    input_objects = []
    interface_node_list = []
    add_header = True
    input_object_header = True
    interface_node_header = True
    input_object_counter = 1
    field_counter = 1

    payload_counter = 1
    for key in introspect_dict:
        if key == "__schema":
            for value  in introspect_dict[key]:
                if value == 'types':
                    list = introspect_dict[key][value]
                    node_count = 1
                    for list_value in list:

                        for list_key in list_value:
                            if list_key == 'name' and list_value[list_key] == 'JobSeekerMutationRoot':
                                paragraphs.append(Spacer(1, 12))
                                # paragraphs.append(doHeading('<b>Mutations of Admin Entity</b>', h4))
                                field_value = list_value['fields']
                                count = 1
                                for key_field_value in field_value:
                                    # paragraphs.append(Paragraph('<b>%d.</b> %s' % (count, key_field_value['name'] ), ParagraphStyle('Normal')))
                                    # Add the details of mutation in the mutation class
                                    paragraphs2.append(Mutation(key_field_value['name'],key_field_value['description'], (key_field_value['args'][0].values()[1]), (key_field_value['args'][0].values()[2].values()[2].values()[1]),key_field_value['type'].values()[1]))
                                    # if (key_field_value['description']):
                                    #     paragraphs.append(Paragraph('description : %s' % (key_field_value['description']), ParagraphStyle('Normal')))
                                    # paragraphs.append(Paragraph('Mutation input name: ', t1))
                                    # paragraphs.append(Spacer(12,1))
                                    # paragraphs.append(Paragraph('name: %s' % (key_field_value['args'][0].values()[0]),t1))
                                    # paragraphs.append(Paragraph('%s' % (key_field_value['args'][0].values()[2].values()[2].values()[1]),t2))
                                    # if (key_field_value['args'][0].values()[1]):
                                    #     paragraphs.append(Paragraph('%s' % (key_field_value['args'][0].values()[1]),t2))

                                    input_objects.append(key_field_value['args'][0].values()[2].values()[2].values()[1])
                                    # paragraphs.append(Paragraph('ofType: %s' % (key_field_value['args'][0].values()[2].values()[2].values()[2]),t3))
                                    # paragraphs.append(Paragraph('defaultValue: %s' % (key_field_value['args'][0].values()[3]), t1))
                                    # paragraphs.append(Paragraph('Mutation payload name: ', t1))
                                    # paragraphs.append(Paragraph('%s' % (key_field_value['type'].values()[1]), t2))
                                    payload_list.append(key_field_value['type'].values()[1])
                                    # paragraphs.append(Spacer(1,12))
                                    # count +=1

                            # if list_key == 'name' and list_value[list_key] in input_objects:
                            if list_key == 'kind' and list_value[list_key] == "INPUT_OBJECT":

                                # if list_value['name'] in input_objects:
                                #     paragraphs.append(Paragraph('Fields required in mutation input: ', t2))
                                # if input_object_header == True:
                                #     paragraphs.append(doHeading('<b>Input object relations:</b>', h4))
                                #     input_object_header = False
                                # paragraphs.append(Paragraph('<b>%d</b>name: %s' % (input_object_counter, list_value[list_key]), ParagraphStyle('Normal')))
                                # paragraphs.append(Paragraph('kind: %s' % list_value['kind'], ParagraphStyle('Normal')))
                                input_field_values = list_value['inputFields']

                                input_field_cnt = 1
                                paragraphs.append(Paragraph('<b>-</b> %s' % list_value['name'], t2))
                                for input_field_val_el in input_field_values:
                                    if (input_field_val_el['type'].values()[1]):
                                        paragraphs.append(Paragraph('<b>*</b> %s (%s)' % (
                                        input_field_val_el['name'], input_field_val_el['type'].values()[1]), t3))
                                    else:
                                        if (input_field_val_el['type'].values()[2]['name']):
                                            paragraphs.append(Paragraph('<b>*</b> %s (%s)' % (input_field_val_el['name'], input_field_val_el['type'].values()[2]['name']),t3))
                                        else:
                                            paragraphs.append(
                                                Paragraph('<b>*</b> %s' % (input_field_val_el['name']), t3))
                                    field_counter += 1
                                    input_field_cnt += 1

                                paragraphs.append(Spacer(1,12))


                                input_object_counter +=1

                            if list_key == 'name' and list_value[list_key] in payload_list:
                                # print list_value['name']
                                if add_header == True:
                                    paragraphs.append(doHeading('<b>Mutations of Job Seeker Entity</b>', h4))
                                    add_header = False
                                # paragraphs.append(Paragraph('<b>%d.</b>kind: %s' %(payload_counter, list_value['kind']), ParagraphStyle('Normal')))

                                # Add paragrah3 with paragraps at here and clear paragraph3.
                                paragraphs = paragraphs + paragraph3
                                del paragraph3[:]

                                for mutation_el in paragraphs2:
                                    if mutation_el.payload == list_value[list_key]:
                                        if payload_counter != 1:
                                            paragraphs.append(Spacer(1, 12))
                                        paragraphs.append(Paragraph('<b>%d.</b> %s' % (payload_counter, mutation_el.name), ParagraphStyle('Normal')))
                                        if (mutation_el.desc):
                                            paragraphs.append(
                                                Paragraph('Description : %s' % (mutation_el.desc), t1))
                                            paragraphs.append(Spacer(1, 12))

                                        paragraphs.append(Paragraph('Mutation inputs name: ', t1))
                                        # paragraphs.append(Spacer(1, 12))
                                        # paragraphs.append(Paragraph('%s' % (mutation_el.input),t2))

                                        # from here the data is appended to paragraph3 to adjust the content in the paragraph.
                                        if (mutation_el.arg_desc):
                                            paragraph3.append(Paragraph('Args description: %s' % (mutation_el.arg_desc),t2))
                                            paragraph3.append(Spacer(1, 12))
                                        paragraph3.append(Paragraph('Mutation payload name: ', t1))
                                        paragraph3.append(Paragraph('%s' % (mutation_el.payload), t2))

                                        fields_value_list = list_value['fields']
                                        # paragraph3.append(Paragraph('Fields required:', t2))
                                        fields_cnt = 1
                                        for fields_value_list_el in fields_value_list:
                                            if (fields_value_list_el['type'].values()[1]):
                                                paragraph3.append(
                                                    Paragraph('<b>-</b> %s (%s)' % (fields_value_list_el['name'], fields_value_list_el['type'].values()[1]), t3))
                                            else:
                                                paragraph3.append(
                                                    Paragraph('<b>-</b> %s' % (fields_value_list_el['name']), t3))
                                            fields_cnt += 1
                                        paragraph3.append(Spacer(1, 12))
                                        break


                                paragraph3.append(Paragraph('Mutation description:', t1))
                                paragraph3.append(Paragraph('Name: ', t2))
                                paragraph3.append(Paragraph('%s' % (list_value['name']), t3))

                                payload_detail = list_value['description']
                                payload_counter += 1

                                if (payload_detail):
                                    zero_point = payload_detail.find('EventRegistrationStatus')


                                    first_point = payload_detail.find("Description")

                                    second_point = payload_detail.find("Feature")
                                    third_point = payload_detail.find("Sample Request")
                                    if third_point == -1:
                                        third_point = payload_detail.find("Example Request")

                                    fourth_point = payload_detail.find('Sample Input')
                                    if fourth_point == -1:
                                        fourth_point = payload_detail.find('Example Input')
                                        if fourth_point == -1:
                                            fourth_point = payload_detail.find('Variable Input')

                                    fifth_point = payload_detail.find('File Inputs')
                                    sixth_point = payload_detail.find('Error Codes')
                                    event_reg_status = ''

                                    if zero_point != -1:
                                        detail = payload_detail[0:zero_point]
                                        if first_point != -1:
                                            event_reg_status = payload_detail[zero_point+ len('EventRegistrationStatus:'):first_point]
                                        else:
                                            detail = ''

                                    else:
                                        if first_point != -1:
                                            detail = payload_detail[0:first_point]
                                        else:
                                            detail = ''

                                    if second_point != -1:
                                        description = payload_detail[first_point + len("Description:\n"):second_point]
                                        feature = payload_detail[second_point + len("Feature:"):third_point]
                                    else:
                                        feature = ''
                                        description = payload_detail[first_point + len("Description:\n"):third_point]


                                    sample_request = payload_detail[third_point+ len('Sample Request:\n'):fourth_point]

                                    if fifth_point != -1:
                                        varrible_input = payload_detail[fourth_point + len('Sample Input :  \n'): fifth_point]
                                        if sixth_point != -1:
                                            file_input = payload_detail[fifth_point+ len('File Inputs:'): sixth_point]
                                        else:
                                            file_input = payload_detail[fifth_point + len('File Inputs:'): len(payload_detail) ]
                                    else:
                                        if sixth_point != -1:
                                            varrible_input = payload_detail[fourth_point + len('Sample Input:\n'): sixth_point]
                                        else:
                                            varrible_input = payload_detail[fourth_point + len('Sample Input:\n'): len(payload_detail)]
                                        file_input =''

                                    if sixth_point != -1:
                                        error_codes = payload_detail[sixth_point + len('Error Codes:\n'): len(payload_detail)]
                                    else:
                                        error_codes = ''

                                    event_reg_sta_list = event_reg_status.splitlines()
                                    file_input_list = file_input.splitlines()
                                    error_codes_list = error_codes.splitlines()

                                    sample_request_list = sample_request.splitlines()
                                    sample_input_list = varrible_input.splitlines()

                                    # paragraphs.append(Paragraph('description:', ParagraphStyle('Normal')))
                                    paragraph3.append(Paragraph('Detail:', t2))
                                    paragraph3.append(Paragraph('%s' % detail, t3))
                                    if (event_reg_sta_list):
                                        paragraph3.append(Paragraph('Event register status:', t2))
                                        for event_reg_sta_el in event_reg_sta_list:
                                            paragraph3.append(Paragraph('%s' % event_reg_sta_el, t3))
                                    if (description):
                                        paragraph3.append(Paragraph('Description:', t2))
                                        paragraph3.append(Paragraph('%s' % (description), t3))

                                    if (feature):
                                        paragraph3.append(Paragraph('Feature:',t2))
                                        paragraph3.append(Paragraph('%s' % feature, t3))

                                    # #

                                    paragraph3.append(Paragraph('Sample Request: ', t2))
                                    left_indent = 60
                                    paragraph3.append(Paragraph('<b>\"</b>',ParagraphStyle('Normal', leftIndent = 60) ))
                                    for sam_req_el in sample_request_list:
                                        if sam_req_el.find("{") != -1:
                                            paragraph3.append(Paragraph('%s' % sam_req_el, ParagraphStyle('Normal', leftIndent = left_indent)))
                                            left_indent += 10
                                        elif sam_req_el.find("}") != -1:
                                            left_indent -= 10
                                            paragraph3.append(Paragraph('%s' % sam_req_el, ParagraphStyle('Normal', leftIndent = left_indent)))
                                        else:
                                            paragraph3.append(Paragraph('%s' % sam_req_el, ParagraphStyle('Normal', leftIndent=left_indent)))
                                    paragraph3.append(Paragraph('<b>\"</b>',ParagraphStyle('Normal', leftIndent = 60) ))

                                    # paragraphs.append(Paragraph('%s' % sample_request, t2))
                                    paragraph3.append(Paragraph('Sample Input: ', t2))
                                    left_indent = 60
                                    paragraph3.append(Paragraph('<b>\"</b>',ParagraphStyle('Normal', leftIndent = 60) ))
                                    for sam_in_el in sample_input_list:
                                        if sam_in_el.find("{") != -1:
                                            paragraph3.append(Paragraph('%s' % sam_in_el, ParagraphStyle('Normal', leftIndent = left_indent)))
                                            left_indent += 10
                                        elif sam_in_el.find("}") != -1:
                                            left_indent -= 10
                                            paragraph3.append(Paragraph('%s' % sam_in_el, ParagraphStyle('Normal', leftIndent = left_indent)))
                                        else:
                                            paragraph3.append(Paragraph('%s' % sam_in_el, ParagraphStyle('Normal', leftIndent= left_indent)))

                                    paragraph3.append(Paragraph('<b>\"</b>',ParagraphStyle('Normal', leftIndent = 60) ))
                                    # paragraphs.append(Paragraph('%s' % varrible_input, t2))
                                    if (file_input_list):
                                        paragraph3.append(Paragraph('File Inputs: ', t2))
                                        for file_in_el in file_input_list:
                                            if (not re.match(r"[ \t]*$", file_in_el)):
                                                paragraph3.append(Paragraph('<b>-</b> %s' %file_in_el, t3))
                                    if (error_codes_list):
                                        paragraph3.append(Paragraph('Error Codes:',t2))
                                        for err_el in error_codes_list:
                                            if (not re.match(r"[ \t]*$", err_el)):
                                                paragraph3.append(Paragraph('<b>-</b> %s' % err_el, t3))



                                        # print fields_value_list_el['name']

                                # paragraphs.append(Spacer(1, 12))



                            if list_key == 'name' and list_value[list_key] == 'Query_JobSeeker':
                                field_value = list_value['fields']
                                count = 1
                                paragraphs.append(doHeading('<b>JobSeeker quaries:</b>', h4))
                                for key_field_value in field_value:
                                    paragraphs.append(Paragraph('<b>%d.</b> Name : %s' % (count, key_field_value['name']), ParagraphStyle('Normal') ))
                                    paragraphs.append(Paragraph('description : %s' % (key_field_value['description']), ParagraphStyle('Normal')))
                                    # paragraphs.append(Paragraph('args : ', ParagraphStyle('Normal')))
                                    # args_list = key_field_value['args']
                                    # for args_list_el in args_list:
                                    #     paragraphs.append(Paragraph('name: %s' % args_list_el['name'], t1))
                                    #     paragraphs.append(Paragraph('description: %s' % args_list_el['description'], t1))
                                    #
                                    # paragraphs.append(Paragraph('Type : ', ParagraphStyle('Normal')))
                                    # paragraphs.append(Paragraph('name: %s' % key_field_value['type'].values()[1], t1))
                                    # paragraphs.append(Paragraph('kind: %s' % key_field_value['type'].values()[0], t1))


                                    # paragraphs.append(Paragraph('Is Deprecated : %s' % (key_field_value['isDeprecated']),ParagraphStyle('Normal')))
                                    # paragraphs.append(Paragraph('Deprecation Reason : %s' % (key_field_value['deprecationReason']),ParagraphStyle('Normal')))
                                    paragraphs.append(Spacer(1, 12))
                                    count +=1


                            if list_value[list_key] == 'INTERFACE' and list_value['name'] == 'Node':
                                paragraphs.append(doHeading('<b>Interface nodes (Job seeker):</b>', h4))
                                paragraphs.append(Paragraph('Name: %s' % list_value['name'], ParagraphStyle('Normal')))
                                paragraphs.append(Paragraph('Kind: %s' % list_value['kind'], ParagraphStyle('Normal')))
                                paragraphs.append(Paragraph('Description: %s' % list_value['description'], ParagraphStyle('Normal')))
                                paragraphs.append(Paragraph('Fields:', ParagraphStyle('Normal')))

                                interface_field_list = list_value['fields']
                                for interface_field_list_el in interface_field_list:
                                    # paragraphs.append(Paragraph('name: %s' % interface_field_list_el['name'], t1))
                                    paragraphs.append(Paragraph('description: %s' % interface_field_list_el['description'], t1))

                                # paragraphs.append(Paragraph('Input fields: %s' % list_value['inputFields'], ParagraphStyle('Normal')))
                                # paragraphs.append(Paragraph('Intrefaces: %s' % list_value['interfaces'], ParagraphStyle('Normal')))
                                # paragraphs.append(Paragraph('Enum values: %s' % list_value['enumValues'], ParagraphStyle('Normal')))
                                paragraphs.append(Paragraph('Possible interface types: ', ParagraphStyle('Normal')))


                                count = 1;
                                possible_types = list_value['possibleTypes']
                                for value_possible_type in possible_types:
                                    paragraphs.append(Paragraph('<b>-</b> %s' % ( value_possible_type['name']), t1 ))
                                    interface_node_list.append(value_possible_type['name'])
                                    count += 1

                            if list_key == 'name' and list_value[list_key] in interface_node_list:
                                if interface_node_header:
                                    paragraphs.append(Spacer(1, 12))
                                    paragraphs.append(doHeading('<b>Available interface nodes (Job seeker). </b>', h4))
                                    interface_node_header = False

                                paragraphs.append(Paragraph('<b>-</b> %s' % ( list_value['name']), t1))
                                if (list_value['description']):
                                    paragraphs.append(Paragraph('<b>description: </b> %s' % (list_value['description']), t2))
                                list_node_fields = list_value['fields']
                                # if (list_node_fields):
                                #     paragraphs.append(Paragraph('Fields:', t2))
                                for list_node_fields_el in list_node_fields:
                                    if (list_node_fields_el.values()[3]['name']):
                                        paragraphs.append(Paragraph('<b>*</b> %s (%s)' % (list_node_fields_el.values()[0], list_node_fields_el.values()[3]['name']), t3))
                                        if (list_node_fields_el.values()[1]):
                                            paragraphs.append(Paragraph('description: %s' % (list_node_fields_el.values()[1]), t4))
                                    else:
                                        if (list_node_fields_el.values()[3]['ofType'].values()[1]):
                                            paragraphs.append(Paragraph('<b>*</b> %s (%s)' % (list_node_fields_el.values()[0], list_node_fields_el.values()[3]['ofType'].values()[1]), t3))
                                        else:
                                            paragraphs.append(Paragraph('<b>*</b> %s' % (list_node_fields_el.values()[0]), t3))
                                        if (list_node_fields_el.values()[1]):
                                            paragraphs.append(Paragraph('description: %s' % (list_node_fields_el.values()[1]),t4))
                                # if (list_value['description']):
                                #     paragraphs.append(Paragraph('description: %s' % list_value['description'], ParagraphStyle('Normal')))
                                paragraphs.append(Spacer(1,12))
                                node_count +=1

    #Add the remaining content in paragraph3
    paragraphs = paragraphs + paragraph3

    # paragraphs.append(Paragraph("This is first content", ParagraphStyle('Normal')))
    # paragraphs.append(Paragraph('Interface nodes', h4))
    # paragraphs.append(Paragraph('Admin mutation root', h4))
    # print payload_list
    # print input_objects
    # paragraphs.append(doHeading('<b>Input object relations:</b>', h4))
    # paragraphs.append(PageBreak())

    # doc = IntroSpectDocTemplate('server_jobseeker.pdf')
    # doc.multiBuild(paragraphs)
    return  paragraphs

def create_introspect_doc():
    front_page = create_front_page()
    toc_page = create_toc_page()
    admin_page = introspect_schema_admin()
    jobseeker_page = introspect_schema_jobseeker()

    doc = IntroSpectDocTemplate('schema_introspect.pdf')
    doc.multiBuild((front_page + toc_page + admin_page + jobseeker_page))
    # canvasmaker = NumberedCanvas


# def introspect_schema_jobseeker():
#     paragraphs = []
#     paragraphs.append(toc)
#
#     paragraphs.append(Paragraph('<b>Table of contents</b>', centred))
#     paragraphs.append(PageBreak())
#
#     introspect_dict = SCHEMA_JOBSEEKER.introspect()
#     payload_list = []
#     payload_counter = 1
#     add_header = True
#     for key in introspect_dict:
#         if key == "__schema":
#             for value in introspect_dict[key]:
#                 if value == 'types':
#                     list = introspect_dict[key][value]
#                     for list_value in list:
#                         for list_key in list_value:
#                             if list_key == 'name' and list_value[list_key] == 'JobSeekerMutationRoot':
#                                 paragraphs.append(doHeading('<b>JobSeeker mutation root:</b> ', h4))
#                                 field_value = list_value['fields']
#                                 count = 1
#                                 for key_field_value in field_value:
#                                     paragraphs.append(Paragraph('<b>%d.</b> name : %s' % (count, key_field_value['name'] ), ParagraphStyle('Normal')))
#                                     paragraphs.append(Paragraph('description : %s' % (key_field_value['description']), ParagraphStyle('Normal')))
#                                     paragraphs.append(Paragraph('args : ', ParagraphStyle('Normal')))
#                                     paragraphs.append(Spacer(12,1))
#                                     paragraphs.append(Paragraph('name: %s' % (key_field_value['args'][0].values()[0]),t1))
#                                     paragraphs.append(Paragraph('description: %s' % (key_field_value['args'][0].values()[1]),t1))
#                                     paragraphs.append(Paragraph('type : ', t1))
#                                     paragraphs.append(Paragraph('kind: %s' % (key_field_value['args'][0].values()[2].values()[0]),t2))
#                                     paragraphs.append(Paragraph('name: %s' % (key_field_value['args'][0].values()[2].values()[1]),t2))
#                                     paragraphs.append(Paragraph('ofType: ',t2))
#                                     paragraphs.append(Paragraph('kind: %s' % (key_field_value['args'][0].values()[2].values()[2].values()[0]),t3))
#                                     paragraphs.append(Paragraph('name: %s' % (key_field_value['args'][0].values()[2].values()[2].values()[1]),t3))
#                                     paragraphs.append(Paragraph('ofType: %s' % (key_field_value['args'][0].values()[2].values()[2].values()[2]),t3))
#                                     paragraphs.append(Paragraph('defaultValue: %s' % (key_field_value['args'][0].values()[3]), t1))
#                                     paragraphs.append(Paragraph('type : ', ParagraphStyle('Normal')))
#                                     paragraphs.append(Paragraph('kind : %s' % (key_field_value['type'].values()[0]), t1))
#                                     paragraphs.append(Paragraph('name : %s' % (key_field_value['type'].values()[1]), t1))
#                                     payload_list.append(key_field_value['type'].values()[1])
#                                     paragraphs.append(Paragraph('ofType : %s' % (key_field_value['type'].values()[2]),t1))
#                                     paragraphs.append(Paragraph('Is Deprecated : %s' % (key_field_value['isDeprecated']), ParagraphStyle('Normal')))
#                                     paragraphs.append(Paragraph('Deprecation Reason : %s' % (key_field_value['deprecationReason']), ParagraphStyle('Normal')))
#                                     paragraphs.append(Spacer(1,12))
#                                     count +=1
#
#                             if list_key == 'name' and list_value[list_key] in payload_list:
#                                 # print list_value['name']
#                                 if add_header == True:
#                                     paragraphs.append(doHeading('<b>Mutation payload:</b>', h4))
#                                     add_header = False
#                                 paragraphs.append(Paragraph('<b>%d.</b>kind: %s' %(payload_counter, list_value['kind']), ParagraphStyle('Normal')))
#                                 paragraphs.append(Paragraph('name: %s' %  list_value['name'], ParagraphStyle('Normal')))
#
#                                 payload_detail = list_value['description']
#
#                                 if (payload_detail):
#                                     zero_point = payload_detail.find('EventRegistrationStatus')
#                                     first_point = payload_detail.find("Description")
#
#                                     second_point = payload_detail.find("Feature")
#                                     third_point = payload_detail.find("Sample Request")
#                                     if third_point == -1:
#                                         third_point = payload_detail.find("Example Request")
#
#                                     fourth_point = payload_detail.find('Sample Input')
#                                     if fourth_point == -1:
#                                         fourth_point = payload_detail.find('Example Input')
#
#                                     fifth_point = payload_detail.find('File Inputs')
#                                     sixth_point = payload_detail.find('Error Codes')
#
#                                     event_reg_status = ''
#                                     detail = ''
#
#                                     if zero_point != -1:
#                                         detail = payload_detail[0:zero_point]
#                                         if first_point != -1:
#                                             event_reg_status = payload_detail[zero_point+ len('EventRegistrationStatus:'):first_point]
#                                         else:
#                                             detail = ''
#                                     else:
#                                         if first_point != -1:
#                                             detail = payload_detail[0:first_point]
#                                         else:
#                                             detail = ''
#
#                                     if second_point != -1:
#                                         description = payload_detail[first_point + len("Description:\n"):second_point]
#                                         feature = payload_detail[second_point + len("Feature:"):third_point]
#                                     else:
#                                         feature = ''
#                                         description = payload_detail[first_point + len("Description:\n"):third_point]
#
#
#                                     sample_request = payload_detail[third_point+ len('Sample Request:\n'):fourth_point]
#
#                                     if fifth_point != -1:
#                                         varrible_input = payload_detail[fourth_point + len('Sample Input:\n'): fifth_point]
#                                         if sixth_point != -1:
#                                             file_input = payload_detail[fifth_point+ len('File Inputs:'): sixth_point]
#                                         else:
#                                             file_input = payload_detail[fifth_point + len('File Inputs:'): len(payload_detail) ]
#                                     else:
#                                         if sixth_point != -1:
#                                             varrible_input = payload_detail[fourth_point + len('Sample Input:\n'): sixth_point]
#                                         else:
#                                             varrible_input = payload_detail[fourth_point + len('Sample Input:\n'): len(payload_detail)]
#                                         file_input =''
#
#                                     if sixth_point != -1:
#                                         error_codes = payload_detail[sixth_point + len('Error Codes:\n'): len(payload_detail)]
#                                     else:
#                                         error_codes = ''
#
#                                     event_reg_sta_list = event_reg_status.splitlines()
#                                     file_input_list = file_input.splitlines()
#                                     error_codes_list = error_codes.splitlines()
#
#                                     sample_request_list = sample_request.splitlines()
#                                     sample_input_list = varrible_input.splitlines()
#
#                                     paragraphs.append(Paragraph('description:', ParagraphStyle('Normal')))
#                                     paragraphs.append(Paragraph('description: %s' % detail, t1))
#                                     paragraphs.append(Paragraph('Event register status:', t1))
#                                     for event_reg_sta_el in event_reg_sta_list:
#                                         paragraphs.append(Paragraph('%s' % event_reg_sta_el, t2))
#                                     paragraphs.append(Paragraph('Description: %s' %description, t1))
#                                     paragraphs.append(Paragraph('Feature: %s' % feature, t1))
#                                     paragraphs.append(Paragraph('Sample Request: ', t1))
#                                     left_indent = 40
#                                     for sam_req_el in sample_request_list:
#                                         if sam_req_el.find("{") != -1:
#                                             paragraphs.append(Paragraph('%s' % sam_req_el,
#                                                                         ParagraphStyle('Normal', leftIndent=left_indent)))
#                                             left_indent += 10
#                                         elif sam_req_el.find("}") != -1:
#                                             left_indent -= 10
#                                             paragraphs.append(Paragraph('%s' % sam_req_el,
#                                                                         ParagraphStyle('Normal', leftIndent=left_indent)))
#                                         else:
#                                             paragraphs.append(Paragraph('%s' % sam_req_el,
#                                                                         ParagraphStyle('Normal', leftIndent=left_indent)))
#                                     # paragraphs.append(Paragraph('%s' % sample_request, t2))
#
#                                     paragraphs.append(Paragraph('Sample Input: ', t1))
#                                     left_indent = 40
#                                     for sam_in_el in sample_input_list:
#                                         if sam_in_el.find("{") != -1:
#                                             paragraphs.append(Paragraph('%s' % sam_in_el,
#                                                                         ParagraphStyle('Normal', leftIndent=left_indent)))
#                                             left_indent += 10
#                                         elif sam_in_el.find("}") != -1:
#                                             left_indent -= 10
#                                             paragraphs.append(Paragraph('%s' % sam_in_el,
#                                                                         ParagraphStyle('Normal', leftIndent=left_indent)))
#                                         else:
#                                             paragraphs.append(Paragraph('%s' % sam_in_el,
#                                                                         ParagraphStyle('Normal', leftIndent=left_indent)))
#                                     # paragraphs.append(Paragraph('%s' % varrible_input, t2))
#                                     paragraphs.append(Paragraph('File Inputs: ', t1))
#                                     for file_in_el in file_input_list:
#                                         paragraphs.append(Paragraph('%s' %file_in_el, t2))
#                                     paragraphs.append(Paragraph('Error Codes:',t1))
#                                     for err_el in error_codes_list:
#                                         paragraphs.append(Paragraph('%s' % err_el, t2))
#                                     paragraphs.append(Spacer(1, 12))
#
#                                     payload_counter +=1
#
#                             if list_key == 'name' and list_value[list_key] == 'Query_JobSeeker':
#                                 field_value = list_value['fields']
#                                 count = 1
#                                 paragraphs.append(doHeading('<b>Query_JobSeeker:</b>', h4))
#                                 for key_field_value in field_value:
#                                     paragraphs.append(Paragraph('<b>%d.</b> Name : %s' % (count, key_field_value['name']), ParagraphStyle('Normal')))
#                                     paragraphs.append(Paragraph('Description : %s' % (key_field_value['description']), ParagraphStyle('Normal')))
#                                     paragraphs.append(Paragraph('Args : %s' % (key_field_value['args']), ParagraphStyle('Normal')))
#                                     paragraphs.append(Paragraph('Type : %s' % (key_field_value['type']), ParagraphStyle('Normal')))
#                                     paragraphs.append(Paragraph('Is Deprecated : %s' % (key_field_value['isDeprecated']), ParagraphStyle('Normal')))
#                                     paragraphs.append(Paragraph('Deprecation Reason : %s' % (key_field_value['deprecationReason']), ParagraphStyle('Normal')))
#                                     paragraphs.append(Spacer(1, 12))
#                                     count += 1
#
#                             if list_value[list_key] == 'INTERFACE' and list_value['name'] == 'Node':
#                                 paragraphs.append(doHeading('<b>Interface Node:</b>', h4))
#                                 paragraphs.append(Paragraph('Name: %s' % list_value['name'], ParagraphStyle('Normal')))
#                                 paragraphs.append(Paragraph('Kind: %s' % list_value['kind'], ParagraphStyle('Normal')))
#                                 paragraphs.append(Paragraph('Description: %s' % list_value['description'], ParagraphStyle('Normal')))
#                                 paragraphs.append(Paragraph('Fields: %s' % list_value['fields'], ParagraphStyle('Normal')))
#                                 paragraphs.append(Paragraph('Input fields: %s' % list_value['inputFields'], ParagraphStyle('Normal')))
#                                 paragraphs.append(Paragraph('Intrefaces: %s' % list_value['interfaces'], ParagraphStyle('Normal')))
#                                 paragraphs.append(Paragraph('Enum values: %s' % list_value['enumValues'], ParagraphStyle('Normal')))
#                                 paragraphs.append(Paragraph('Possible types: ', ParagraphStyle('Normal')))
#
#                                 count = 1;
#                                 possible_types = list_value['possibleTypes']
#                                 for value_possible_type in possible_types:
#                                     paragraphs.append(Paragraph('<b>%d.</b> Name: %s' % (count, value_possible_type['name']), ParagraphStyle('Normal') ))
#                                     paragraphs.append(Paragraph('Kind: %s' % value_possible_type['kind'], ParagraphStyle('Normal')))
#                                     paragraphs.append(Paragraph('Of type: %s' % value_possible_type['ofType'], ParagraphStyle('Normal')))
#                                     paragraphs.append(Spacer(1, 12))
#                                     count += 1
#
#     paragraphs.append(PageBreak())
#
#     doc = IntroSpectDocTemplate('server_jobseeker.pdf')
#     doc.multiBuild(paragraphs)

def _introspect_shema_admin():
    introspect_dict = SCHEMA_ADMIN.introspect()
    fp = open("introspect_schme_admin.json", "w")
    json.dump(introspect_dict, fp)
    fp.close()

    #write only the mutations
    buf = io.BytesIO()

    #set up the doc with paper size and margin
    doc = SimpleDocTemplate(
        buf,
        rightMargin = inch/2,
        leftMargin=inch / 2,
        topMargin=inch / 2,
        bottomMargin=inch / 2,
        pagesize = letter
    )

    #styling paragraph
    styles = getSampleStyleSheet()
    paragraphs = []
    # paragraphs.append(Paragraph('This is a paragraph', styles['Normal']))

    node_list = []
    for key in introspect_dict:
        if key == "__schema":
            for value  in introspect_dict[key]:
                if value == 'types':
                    list = introspect_dict[key][value]
                    for list_value in list:
                        for list_key in list_value:
                            if list_key == 'name' and list_value[list_key] == 'AdminMutationRoot':
                                paragraphs.append(Paragraph('AdminMutationRoot:' , styles['Heading4']))
                                field_value = list_value['fields']
                                count = 1
                                for key_field_value in field_value:
                                    paragraphs.append(Paragraph('%d. Name : %s' % (count, key_field_value['name'] ), styles['Normal']))
                                    paragraphs.append(Paragraph('Description : %s' % (key_field_value['description']), styles['Normal']))
                                    paragraphs.append(Paragraph('Args : %s' % (key_field_value['args']), styles['Normal']))
                                    paragraphs.append(Paragraph('Type : %s' % (key_field_value['type']), styles['Normal']))
                                    paragraphs.append(Paragraph('Is Deprecated : %s' % (key_field_value['isDeprecated']), styles['Normal']))
                                    paragraphs.append(Paragraph('Deprecation Reason : %s' % (key_field_value['deprecationReason']), styles['Normal']))
                                    paragraphs.append(Spacer(1,12))
                                    count +=1

                                # input_field_value = list_value['inputFields']
                                # count2 = 1
                                # for key_field_value in input_field_value:
                                #     fw.write('%d. name : %s\n' % (count2, key_field_value['name'] ))
                                #     fw.write('description : %s\n' % (key_field_value['description']))
                                #     fw.write('type : %s\n' % (key_field_value['type']))
                                #     fw.write('defaultValue : %s\n' % (key_field_value['defaultValue']))
                                #     count2 +=1

                            if list_key == 'name' and list_value[list_key] == 'Query_Admin':
                                field_value = list_value['fields']
                                count = 1
                                paragraphs.append(Paragraph('Query_Admin:', styles['Heading4']))
                                for key_field_value in field_value:
                                    paragraphs.append(Paragraph('%d. Name : %s' % (count, key_field_value['name']), styles['Normal'] ))
                                    paragraphs.append(Paragraph('Description : %s' % (key_field_value['description']), styles['Normal']))
                                    paragraphs.append(Paragraph('Args : %s' % (key_field_value['args']), styles['Normal']))
                                    paragraphs.append(Paragraph('Type : %s' % (key_field_value['type']), styles['Normal']))
                                    paragraphs.append(Paragraph('Is Deprecated : %s' % (key_field_value['isDeprecated']),styles['Normal']))
                                    paragraphs.append(Paragraph('Deprecation Reason : %s' % (key_field_value['deprecationReason']),styles['Normal']))
                                    paragraphs.append(Spacer(1, 12))
                                    count +=1


                            if list_value[list_key] == 'INTERFACE' and list_value['name'] == 'Node':
                                paragraphs.append(Paragraph('Interface Node:', styles['Heading4']))
                                paragraphs.append(Paragraph('Name: %s' % list_value['name'], styles['Normal']))
                                paragraphs.append(Paragraph('Kind: %s' % list_value['kind'], styles['Normal']))
                                paragraphs.append(Paragraph('Description: %s' % list_value['description'], styles['Normal']))
                                paragraphs.append(Paragraph('Fields: %s' % list_value['fields'], styles['Normal']))
                                paragraphs.append(Paragraph('Input fields: %s' % list_value['inputFields'], styles['Normal']))
                                paragraphs.append(Paragraph('Intrefaces: %s' % list_value['interfaces'], styles['Normal']))
                                paragraphs.append(Paragraph('Enum values: %s' % list_value['enumValues'], styles['Normal']))
                                paragraphs.append(Paragraph('Possible types: ', styles['Normal']))

                                count = 1;
                                possible_types = list_value['possibleTypes']
                                for value_possible_type in possible_types:
                                    paragraphs.append(Paragraph('%d. Name: %s' % (count, value_possible_type['name']), styles['Normal'] ))
                                    node_list.append(value_possible_type['name'])
                                    paragraphs.append(Paragraph('Kind: %s' % value_possible_type['kind'], styles['Normal']))
                                    paragraphs.append(Paragraph('Of type: %s' % value_possible_type['ofType'], styles['Normal']))
                                    paragraphs.append(Spacer(1, 12))
                                    count += 1


    # print node_list
    doc.build(paragraphs)
    fw = open("admin_mutations.pdf", "w")
    fw.write(buf.getvalue())
    fw.close()

def _introspect_schema_jobseeker():
    introspect_dict = SCHEMA_JOBSEEKER.introspect()

    # write only the mutations
    buf = io.BytesIO()

    # set up the doc with paper size and margin
    doc = SimpleDocTemplate(
        buf,
        rightMargin=inch / 2,
        leftMargin=inch / 2,
        topMargin=inch / 2,
        bottomMargin=inch / 2,
        pagesize=letter
    )

    # styling paragraph
    styles = getSampleStyleSheet()
    paragraphs = []
    # paragraphs.append(Paragraph('This is a paragraph', styles['Normal']))


    for key in introspect_dict:
        if key == "__schema":
            for value in introspect_dict[key]:
                if value == 'types':
                    list = introspect_dict[key][value]
                    for list_value in list:
                        for list_key in list_value:
                            if list_key == 'name' and list_value[list_key] == 'JobSeekerMutationRoot':
                                paragraphs.append(Paragraph('JobSeekerMutationRoot: ', styles['Heading4']))
                                field_value = list_value['fields']
                                count = 1
                                for key_field_value in field_value:
                                    paragraphs.append(Paragraph('%d. Name : %s' % (count, key_field_value['name']), styles['Normal']))
                                    paragraphs.append(Paragraph('Description : %s' % (key_field_value['description']), styles['Normal']))
                                    paragraphs.append(Paragraph('Args : %s' % (key_field_value['args']), styles['Normal']))
                                    paragraphs.append(Paragraph('Type : %s' % (key_field_value['type']), styles['Normal']))
                                    paragraphs.append(Paragraph('Is Deprecated : %s' % (key_field_value['isDeprecated']), styles['Normal']))
                                    paragraphs.append(Paragraph('Deprecation Reason : %s' % (key_field_value['deprecationReason']), styles['Normal']))
                                    paragraphs.append(Spacer(1, 12))
                                    count += 1

                            if list_key == 'name' and list_value[list_key] == 'Query_JobSeeker':
                                field_value = list_value['fields']
                                count = 1
                                paragraphs.append(Paragraph('Query_JobSeeker:', styles['Heading4']))
                                for key_field_value in field_value:
                                    paragraphs.append(Paragraph('%d. Name : %s' % (count, key_field_value['name']), styles['Normal']))
                                    paragraphs.append(Paragraph('Description : %s' % (key_field_value['description']), styles['Normal']))
                                    paragraphs.append(Paragraph('Args : %s' % (key_field_value['args']), styles['Normal']))
                                    paragraphs.append(Paragraph('Type : %s' % (key_field_value['type']), styles['Normal']))
                                    paragraphs.append(Paragraph('Is Deprecated : %s' % (key_field_value['isDeprecated']), styles['Normal']))
                                    paragraphs.append(Paragraph('Deprecation Reason : %s' % (key_field_value['deprecationReason']), styles['Normal']))
                                    paragraphs.append(Spacer(1, 12))
                                    count += 1

                            if list_value[list_key] == 'INTERFACE' and list_value['name'] == 'Node':
                                paragraphs.append(Paragraph('Interface Node:', styles['Heading4']))
                                paragraphs.append(Paragraph('Name: %s' % list_value['name'], styles['Normal']))
                                paragraphs.append(Paragraph('Kind: %s' % list_value['kind'], styles['Normal']))
                                paragraphs.append(Paragraph('Description: %s' % list_value['description'], styles['Normal']))
                                paragraphs.append(Paragraph('Fields: %s' % list_value['fields'], styles['Normal']))
                                paragraphs.append(Paragraph('Input fields: %s' % list_value['inputFields'], styles['Normal']))
                                paragraphs.append(Paragraph('Intrefaces: %s' % list_value['interfaces'], styles['Normal']))
                                paragraphs.append(Paragraph('Enum values: %s' % list_value['enumValues'], styles['Normal']))
                                paragraphs.append(Paragraph('Possible types: ', styles['Normal']))

                                count = 1;
                                possible_types = list_value['possibleTypes']
                                for value_possible_type in possible_types:
                                    paragraphs.append(Paragraph('%d. Name: %s' % (count, value_possible_type['name']), styles['Normal'] ))
                                    paragraphs.append(Paragraph('Kind: %s' % value_possible_type['kind'], styles['Normal']))
                                    paragraphs.append(Paragraph('Of type: %s' % value_possible_type['ofType'], styles['Normal']))
                                    paragraphs.append(Spacer(1, 12))
                                    count += 1

    doc.build(paragraphs)
    fw = open("jobseeker_mutations.pdf", "w")
    fw.write(buf.getvalue())
    fw.close()


# _introspect_shema_admin()
# _introspect_schema_jobseeker()
# create_front_page()
# introspect_schema_admin()
# introspect_schema_jobseeker()

#call to create document
create_introspect_doc()

def check():
    a = []
    a.append(1)
    a.append(2)
    a.append(3)

    print  a
    del a[:]

    print a

# check()