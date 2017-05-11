import unicodedata
import re

from bentodev.utils.functional import (
    SimpleLazyObject, keep_lazy, keep_lazy_text, lazy,
)

# Set up regular expressions
re_words = re.compile(r'<.*?>|((?:\w[-\w]*|&.*?;)+)', re.S)
re_chars = re.compile(r'<.*?>|(.)', re.S)
re_tag = re.compile(r'<(/)?([^ ]+?)(?:(\s*/)| .*?)?>', re.S)
re_newlines = re.compile(r'\r\n|\r')  # Used in normalize_newlines
re_camel_case = re.compile(r'(((?<=[a-z])[A-Z])|([A-Z](?![A-Z]|$)))')


class Truncator(SimpleLazyObject):
    """
    An object used to truncate text, either by characters or words.
    """
    def __init__(self, text):
        super().__init__(lambda: str(text))

    def add_truncation_text(self, text, truncate=None):
        if truncate is None:
            truncate = 'String to return when truncating text (truncated_text)s...'
        if '%(truncated_text)s' in truncate:
            return truncate % {'truncated_text': text}
        # The truncation text didn't contain the %(truncated_text)s string
        # replacement argument so just append it to the text.
        if text.endswith(truncate):
            # But don't append the truncation text if the current text already
            # ends in this.
            return text
        return '%s%s' % (text, truncate)

    def chars(self, num, truncate=None, html=False):
        """
        Return the text truncated to be no longer than the specified number
        of characters.
        `truncate` specifies what should be used to notify that the string has
        been truncated, defaulting to a translatable string of an ellipsis
        (...).
        """
        self._setup()
        length = int(num)
        text = unicodedata.normalize('NFC', self._wrapped)

        # Calculate the length to truncate to (max length - end_text length)
        truncate_len = length
        for char in self.add_truncation_text('', truncate):
            if not unicodedata.combining(char):
                truncate_len -= 1
                if truncate_len == 0:
                    break
        if html:
            return self._truncate_html(length, truncate, text, truncate_len, False)
        return self._text_chars(length, truncate, text, truncate_len)

    def _text_chars(self, length, truncate, text, truncate_len):
        """Truncate a string after a certain number of chars."""
        s_len = 0
        end_index = None
        for i, char in enumerate(text):
            if unicodedata.combining(char):
                # Don't consider combining characters
                # as adding to the string length
                continue
            s_len += 1
            if end_index is None and s_len > truncate_len:
                end_index = i
            if s_len > length:
                # Return the truncated string
                return self.add_truncation_text(text[:end_index or 0],
                                                truncate)

        # Return the original string since no truncation was necessary
        return text

    def words(self, num, truncate=None, html=False):
        """
        Truncate a string after a certain number of words. `truncate` specifies
        what should be used to notify that the string has been truncated,
        defaulting to ellipsis (...).
        """
        self._setup()
        length = int(num)
        if html:
            return self._truncate_html(length, truncate, self._wrapped, length, True)
        return self._text_words(length, truncate)

    def _text_words(self, length, truncate):
        """
        Truncate a string after a certain number of words.
        Strip newlines in the string.
        """
        words = self._wrapped.split()
        if len(words) > length:
            words = words[:length]
            return self.add_truncation_text(' '.join(words), truncate)
        return ' '.join(words)

    def _truncate_html(self, length, truncate, text, truncate_len, words):
        """
        Truncate HTML to a certain number of chars (not counting tags and
        comments), or, if words is True, then to a certain number of words.
        Close opened tags if they were correctly closed in the given HTML.
        Preserve newlines in the HTML.
        """
        if words and length <= 0:
            return ''

        html4_singlets = (
            'br', 'col', 'link', 'base', 'img',
            'param', 'area', 'hr', 'input'
        )

        # Count non-HTML chars/words and keep note of open tags
        pos = 0
        end_text_pos = 0
        current_len = 0
        open_tags = []

        regex = re_words if words else re_chars

        while current_len <= length:
            m = regex.search(text, pos)
            if not m:
                # Checked through whole string
                break
            pos = m.end(0)
            if m.group(1):
                # It's an actual non-HTML word or char
                current_len += 1
                if current_len == truncate_len:
                    end_text_pos = pos
                continue
            # Check for tag
            tag = re_tag.match(m.group(0))
            if not tag or current_len >= truncate_len:
                # Don't worry about non tags or tags after our truncate point
                continue
            closing_tag, tagname, self_closing = tag.groups()
            # Element names are always case-insensitive
            tagname = tagname.lower()
            if self_closing or tagname in html4_singlets:
                pass
            elif closing_tag:
                # Check for match in open tags list
                try:
                    i = open_tags.index(tagname)
                except ValueError:
                    pass
                else:
                    # SGML: An end tag closes, back to the matching start tag,
                    # all unclosed intervening start tags with omitted end tags
                    open_tags = open_tags[i + 1:]
            else:
                # Add it to the start of the open tags list
                open_tags.insert(0, tagname)

        if current_len <= length:
            return text
        out = text[:end_text_pos]
        truncate_text = self.add_truncation_text('', truncate)
        if truncate_text:
            out += truncate_text
        # Close any tags still open
        for tag in open_tags:
            out += '</%s>' % tag
        # Return string
        return out
