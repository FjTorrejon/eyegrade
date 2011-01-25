import xml.dom.minidom as dom
import re

import utils

namespace = 'http://www.it.uc3m.es/jaf/eyegrade/ns/'
text_norm_re = re.compile(r'[\ \t\n]+')

def parse_exam(dom_tree):
    assert dom_tree.nodeType == dom.Node.DOCUMENT_NODE
    root = dom_tree.childNodes[0]
    if get_full_name(root) == (namespace, 'exam'):
        exam = utils.ExamQuestions()
        exam.subject = get_element_content(root, namespace, 'subject')
        exam.degree = get_element_content(root, namespace, 'degree')
        exam.date = get_element_content(root, namespace, 'date')
        exam.duration = get_element_content(root, namespace, 'duration')
        exam.questions = []
        for node in root.getElementsByTagNameNS(namespace, 'question'):
            exam.questions.append(parse_question(node))
    else:
        raise Exception('Error: root element expected to be "exam"')
    return exam

def parse_question(question_node):
    question = utils.Question()
    question.text = get_element_content(question_node, namespace, 'text')
    question.code, code_atts = \
        get_element_content_with_attrs(question_node, namespace, 'code',
                                       ['width', 'position'])
    question.figure, figure_atts = \
        get_element_content_with_attrs(question_node, namespace, 'figure',
                                       ['width', 'position'])
    if question.code is not None and question.figure is not None:
        raise Exception('A question cannot have both figure and code')
    elif question.code is not None:
        if code_atts[1] is None:
            code_atts[1] = 'center'
        elif code_atts[1] != 'center' and code_atts[1] != 'right':
            raise Exception('Incorrect value for attribute "position"')
        if code_atts[0] is None and code_atts[1] == 'right':
            raise Exception('Attribute "width" is mandatory for code '
                            'positioned at the right')
        if code_atts[0] is not None:
            question.annex_width = float(code_atts[0])
        else:
            question.annex_width = None
        question.annex_pos = code_atts[1]
    elif question.figure is not None:
        if figure_atts[1] is None:
            figure_atts[1] = 'center'
        elif figure_atts[1] != 'center' and figure_atts[1] != 'right':
            raise Exception('Incorrect value for attribute "position"')
        if figure_atts[0] is None:
            raise Exception('Attribute "width" is mandatory for figures')
        question.annex_width = float(figure_atts[0])
        question.annex_pos = figure_atts[1]
    choices_list = question_node.getElementsByTagNameNS(namespace, 'choices')
    if len(choices_list) != 1:
        raise Exception('Expected exacly one choices element')
    choices = choices_list[0]
    for node in choices.getElementsByTagNameNS(namespace, 'correct'):
        question.correct_choices.append(get_element_content_node(node))
    for node in choices.getElementsByTagNameNS(namespace, 'incorrect'):
        question.incorrect_choices.append(get_element_content_node(node))
    return question

def get_element_content(parent, namespace, local_name):
    node_list = parent.getElementsByTagNameNS(namespace, local_name)
    if len(node_list) == 1:
        return get_text(node_list[0].childNodes)
    elif len(node_list) == 0:
        return None
    elif len(node_list) > 1:
        raise Exception('Duplicate element: ' + local_name)

def get_element_content_node(element_node):
    return get_text(element_node.childNodes)

def get_element_content_with_attrs(parent, namespace, local_name, attr_names):
    node_list = parent.getElementsByTagNameNS(namespace, local_name)
    if len(node_list) == 1:
        normalize = True if local_name != 'code' else False
        att_vals = []
        for att in attr_names:
            att_vals.append(get_attribute_text(node_list[0], att))
        return (get_text(node_list[0].childNodes, normalize), att_vals)
    elif len(node_list) == 0:
        return None, None
    elif len(node_list) > 1:
        raise Exception('Duplicate element: ' + local_name)

def get_attribute_text(element, attribute_name):
    value = element.getAttributeNS(namespace, attribute_name)
    if value != '':
        return text_norm_re.sub(' ', value.strip())
    else:
        return None

def get_text(node_list, normalize = True):
    data = []
    for node in node_list:
        if node.nodeType == node.TEXT_NODE:
            data.append(node.data)
    if len(data) > 0:
        text = ''.join(data)
        if normalize:
            return text_norm_re.sub(' ', text.strip())
        else:
            return text
    else:
        return None

def get_full_name(element):
    return (element.namespaceURI, element.localName)