# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from breadability.readable import Article
from ..utils import cached_property, fetch_url
from ..models.dom import Sentence, Paragraph, ObjectDocumentModel
from .parser import DocumentParser


class HtmlParser(DocumentParser):
    """Parser of text from HTML format into DOM."""

    SIGNIFICANT_TAGS = (
        "h1", "h2", "h3",
        "b", "strong",
        "big",
        "dfn",
        "em",
    )

    @classmethod
    def from_string(cls, string, url, tokenizer):
        print("string cls : ",cls,"\n")
        return cls(string, tokenizer, url)

    @classmethod
    def from_file(cls, file_path, url, tokenizer):
        print("file cls : ",cls,"\n")
        with open(file_path, "rb") as file:
            return cls(file.read(), tokenizer, url)

    @classmethod
    def from_url(cls, url, tokenizer):
        data = fetch_url(url)
        return cls(data, tokenizer, url)

    def __init__(self, html_content, tokenizer, url=None):
        super(HtmlParser, self).__init__(tokenizer)
        self._article = Article(html_content, url)

    @cached_property
    def significant_words(self):
        words = []
        for paragraph in self._article.main_text:
            for text, annotations in paragraph:
                if self._contains_any(annotations, *self.SIGNIFICANT_TAGS):
                    words.extend(self.tokenize_words(text))

        if words:
            return tuple(words)
        else:
            return self.SIGNIFICANT_WORDS

    @cached_property
    def stigma_words(self):
        words = []
        for paragraph in self._article.main_text:
            for text, annotations in paragraph:
                if self._contains_any(annotations, "a", "strike", "s"):
                    words.extend(self.tokenize_words(text))

        if words:
            return tuple(words)
        else:
            return self.STIGMA_WORDS

    def _contains_any(self, sequence, *args):
        if sequence is None:
            return False

        for item in args:
            if item in sequence:
                return True

        return False

    @cached_property
    def document(self):
        # "a", "abbr", "acronym", "b", "big", "blink", "blockquote", "cite", "code",
        # "dd", "del", "dfn", "dir", "dl", "dt", "em", "h", "h1", "h2", "h3", "h4",
        # "h5", "h6", "i", "ins", "kbd", "li", "marquee", "menu", "ol", "pre", "q",
        # "s", "samp", "strike", "strong", "sub", "sup", "tt", "u", "ul", "var",

        annotated_text = self._article.main_text
        test = 0
        paragraphs = []
        for paragraph in annotated_text:
            sentences = []

            current_text = ""
            for text, annotations in paragraph:
                if annotations and ("h1" in annotations or "h2" in annotations or "h3" in annotations):
                    sentences.append(Sentence(text, self._tokenizer, is_heading=True))
                # skip <pre> nodes
                elif not (annotations and "pre" in annotations):
                    current_text += " " + text

            new_sentences = self.tokenize_sentences(current_text)
            sentences.extend(Sentence(s, self._tokenizer) for s in new_sentences)
            test += len(sentences)
            paragraphs.append(Paragraph(sentences))
        
        if test < 10:
            print("10 문장 이하는 처리하지 않습니다\n")
            exit(1)
        return ObjectDocumentModel(paragraphs)
