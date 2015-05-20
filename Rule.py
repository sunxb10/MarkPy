"""
各种解析转换规则

规则执行的顺序会影响程序结果，以下是经测试正确的顺序：

    1. SpecialChRule
    2. BackslashRule
    3. CodeBlockandParagraphRule
    4. InlineCodeRule
    5. HeaderRule
    6. HrRule
    7. BlockquoteRule
    8. ListRule
    9. ImageRule
    10. LinkRule
    11. EmphasisRule
"""

import re, random, binascii


class SpecialChRule:
    """
    HTML特殊字符<, >, &及HTML标签，此规则必须先于其它所有规则执行
    """
    def __init__(self):
        self._leftangle_pattern = re.compile('<')
        self._rightangle_pattern = re.compile('>')
        # 匹配字符&时必须使用否定预测零宽断言（negative lookahead assertion）以避免破坏HTML实体
        self._ampersand_pattern = re.compile('&(?!#[0-9]+|[a-zA-Z]+|#x[0-9a-fA-F]+;)')
        
    def process(self, block):
        """
        按照规则进行处理
        """ 
        block = self._leftangle_pattern.sub('&lt;', block)
        block = self._rightangle_pattern.sub('&gt;', block)
        block = self._ampersand_pattern.sub('&amp;', block)
        return block



class InlineCodeRule:
    """
    HTML行内代码 <code>
    """
    def __init__(self):
        self._inlinecode_pattern = re.compile('`(.+?)`')

    @classmethod
    def _inlinecode_substring(cls, match):
        """
        行内代码替换函数
        """
        # 替换掉可能会被其它规则错误解析的特殊字符
        substring = match.group(1)
        substring = re.sub('&', '&amp;', substring)
        substring = re.sub('#', '&num;', substring)
        substring = re.sub('_', '&lowbar;', substring)
        substring = re.sub('\*', '&ast;', substring)
        substring = re.sub('\[', '&lbrack;', substring)
        substring = re.sub('\]', '&rbrack;', substring)
        substring = re.sub('\(', '&lpar;', substring)
        substring = re.sub('\)', '&rpar;', substring)
        substring = re.sub('{', '&lbrace;', substring)
        substring = re.sub('}', '&rbrace;', substring)
        substring = re.sub(r'\\', '&bsol;', substring)
        substring = re.sub('!', '&excl;', substring)
        return '<code>%s</code>' % substring

    def process(self, block):
        """
        按照规则进行处理
        """
        block = self._inlinecode_pattern.sub(self._inlinecode_substring, block)
        return block



class CodeBlockandParagraphRule:
    """
    HTML行间代码块 <pre><code> 
    HTML段落 <p>
    """
    def __init__(self):
        self._code_pattern = re.compile('(?<=^)`{3}.*(?=$)', re.M)
        self._inside_code = False  # 记录行间代码块的开始和终止

    @classmethod
    def special_char_sub(cls, line):
        """
        替换代码行中可能会被其它规则错误解析的特殊字符
        """
        substring = line
        substring = re.sub('&', '&amp;', substring)
        substring = re.sub('#', '&num;', substring)
        substring = re.sub('_', '&lowbar;', substring)
        substring = re.sub('\*', '&ast;', substring)
        substring = re.sub('\+', '&plus;', substring)
        substring = re.sub('`', '&grave;', substring)
        substring = re.sub('\[', '&lbrack;', substring)
        substring = re.sub('\]', '&rbrack;', substring)
        substring = re.sub('\(', '&lpar;', substring)
        substring = re.sub('\)', '&rpar;', substring)
        substring = re.sub('{', '&lbrace;', substring)
        substring = re.sub('}', '&rbrace;', substring)
        substring = re.sub(r'\\', '&bsol;', substring)
        substring = re.sub('!', '&excl;', substring)
        substring = re.sub('\.', '&period;', substring)
        substring = re.sub('-', '&#45;', substring)
        return substring

    def process(self, block):
        """
        按照规则进行处理
        """
        new_block = ''
        # 考虑到行间代码有可能整个位于同一block中，因此必须在line level上进行处理
        # 将block切分成行，注意其末尾可能有\n，如此则split('\n')会产生无意义的空白行
        line_list = [line for line in block.split('\n') if line]
        for idx in range(0, len(line_list)):
            line = line_list[idx]
            # print('LINE: ' + line)
            if idx == 0:  # 首行
                match = self._code_pattern.search(line)  # 找```标志
                if match and self._inside_code:  # 结束当前代码块
                    line = '</code></pre>\n</p>'
                    self._inside_code = False
                elif match and not self._inside_code:  # 开启当前代码块
                    line = '<p>\n<pre><code>'
                    self._inside_code = True
                elif not self._inside_code:  # 普通文本行
                    line = '<p>\n' + line
                    if len(line_list) == 1:  # 如果文本块只有一行，还需添加</p>
                        line += '\n</p>'
                else:  # self._inside_code == True，代码行，替换特殊字符
                    line = self.special_char_sub(line)

            elif idx == len(line_list) - 1:  # 末行
                match = self._code_pattern.search(line)  # 找```标志
                if match and self._inside_code:  # 结束当前代码块
                    line = '</code></pre>\n</p>'
                    self._inside_code = False
                elif match and not self._inside_code:  # 开启当前代码块
                    line = '</p>\n<p>\n<pre><code>'  # 需要首先用</p>结束之前的段落再新开<p><pre><code>
                    self._inside_code = True
                elif not self._inside_code:  # 普通文本行
                    line += '\n</p>'
                else:  # self._inside_code == True，代码行，替换特殊字符
                    line = self.special_char_sub(line)

            else:  # 其它行
                match = self._code_pattern.search(line)  # 搜索当前文本行中的```标志
                if match and self._inside_code:  # 当前文本行中有```标志且在行间代码块中，结束当前代码块
                    line = '</code></pre>\n</p>\n<p>'
                    self._inside_code = False                      
                elif match and not self._inside_code:  # 当前文本行中有```标志且不在行间代码块中，开启新的代码块
                    line = '</p>\n<p>\n<code><pre>'
                    self._inside_code = True
                elif self._inside_code: # 当前文本行中没有```标志且在行间代码块中，替换特殊字符
                    line = self.special_char_sub(line)
                else:  # self._inside_code == False，普通文本行
                    pass 
            line += '\n'  # split('\n')切分得到的行本身是没有换行符的，这里添加换行符     
            new_block += line
        return new_block

    def reset(self):
        """
        重置规则
        """
        self._inside_code = False



class HeaderRule:
    """
    HTML标题 <h1>~<h6>
    """
    def __init__(self):
        # Atx风格的<h1>~<h6>标签，根据开头字符#的数目判定层级
        self._atx_pattern = re.compile('(?<=^)(#+)\s+(.+)(?=$)', re.M)
        # Setext风格的<h1>、<h2>标签，根据字符=或-判定层级
        self._setext_pattern = re.compile('(?<=^)\s*(.+)\n([=-]+)\s*(?=$)', re.M)

    @classmethod
    def _atx_substring(cls, match):
        """
        Atx风格的替换函数，Python正则表达式的替换符可以是函数，其参数是match对象
        """
        # 考虑到闭合形式Atx风格标题，标题文字之后可能跟有若干连续的#字符
        header_split_last = match.group(2).split(' ', 1)[-1]
        # 判断标题后是否跟有一连串的#
        if header_split_last == '#' * len(header_split_last):
            titlestring = match.group(2).split(' ', 1)[0]
        else:
            titlestring = match.group(2)
        return '<h%d>%s</h%d>' % (len(match.group(1)), titlestring, len(match.group(1)))

    @classmethod
    def _setext_substring(cls, match):
        """
        Setext风格的替换函数
        """
        if match.group(2)[0] == '=':  # 第二行是字符=
            return '<h1>%s</h1>' % match.group(1)
        elif match.group(2)[0] == '-':  # 第二行是字符-
            return '<h2>%s</h2>' % match.group(1)

    def process(self, block):
        """
        按照规则进行处理
        """
        block = self._atx_pattern.sub(self._atx_substring, block)  # Atx <h1>~<h6>
        block = self._setext_pattern.sub(self._setext_substring, block)  # Setext <h1>、<h2>
        return block


class HrRule:
    """
    HTML水平线 <hr>
    """
    def __init__(self):
        self._hr_1_pattern = re.compile('(?<=^)_{3,}(?=$)', re.M)  # 3个以上连续的下划线
        self._hr_2_pattern = re.compile('(?<=^)\*\s*\*\s*\*(\**|(\s*\*)*)(?=$)', re.M)  # 3个以上星号，中间可以有空格
        self._hr_3_pattern = re.compile('(?<=^)-\s*-\s*-(-*|(\s*-)*)(?=$)', re.M)  # 3个以上减号，中间可以有空格

    def process(self, block):
        """
        按照规则进行处理
        """
        block = self._hr_1_pattern.sub('<hr />', block)
        block = self._hr_2_pattern.sub('<hr />', block)
        block = self._hr_3_pattern.sub('<hr />', block)
        return block



class ListRule:
    """
    HTML列表 <ul>、<ol>
    """
    def __init__(self):
        self._insidelist_unord = False # 记录当前是否在某一无序列表内
        self._insidelist_ord = False  # 记录当前是否在某一有序列表内
        self._list_unord_pattern = re.compile('(?<=^)\s*([\+\-\*])\s+(.+)(?=$)', re.M)
        self._list_ord_pattern = re.compile('(?<=^)\s*(\d+\.)\s+(.+)(?=$)', re.M)

    @classmethod
    def _list_substring(cls, match):
        """
        列表的替换函数
        """
        return '<li>%s</li>\n' % match.group(2)

    def process(self, block):
        """
        按照规则进行处理
        """
        # 先考虑无序列表
        tmp_block_unord = self._list_unord_pattern.sub(self._list_substring, block)
        if self._insidelist_unord:  # 已经在无序列表内
            if tmp_block_unord == block:  # 当前文本块无列表项，结束当前列表
                block = '</ul>\n' + tmp_block_unord
                self._insidelist_unord = False
            else:  # 当前文本块有列表项，延续当前列表
                block = tmp_block_unord
        else:  # 不在无序列表内
            if tmp_block_unord != block:  # 当前文本块有列表项，开始新的无序列表
                block = '<ul>\n' + tmp_block_unord
                self._insidelist_unord = True

        # 再考虑有序列表
        tmp_block_ord = self._list_ord_pattern.sub(self._list_substring, block)           
        if self._insidelist_ord:  # 已经在有序列表内
            if tmp_block_ord == block:  # 当前文本块无列表项，结束当前列表
                block = '</ol>\n' + tmp_block_ord
                self._insidelist_ord = False
            else:  # 当前文本块有列表项，延续当前列表
                block = tmp_block_ord
        else:  # 不在有序列表内
            if tmp_block_ord != block:  # 当前文本块有列表项，开始新的有序列表
                block = '<ol>\n' + tmp_block_ord
                self._insidelist_ord = True
        return block

    def reset(self):
        """
        重置规则
        """
        self._insidelist_unord = False
        self._insidelist_ord = False


class BlockquoteRule:
    """
    HTML区块引用 <blockquote>
    """
    def __init__(self):
        self._insideblockquote = False  # 记录当前是否在某一区块引用内，因为区块引用存在跨文本块的情况
        # 由于HTML特殊字符的原因，使用中会首先调用SpecialChRule将>替换为&gt;
        self._blockquote_pattern = re.compile('(?<=^)&gt;(?=\s+.+$)', re.M)

    def process(self, block):
        """
        按照规则进行处理
        """
        tmp_block = self._blockquote_pattern.sub('', block)  # 去掉开头的字符>（&gt;）
        if self._insideblockquote:  # 当前在区块引用内
            if tmp_block == block:  # 文本未替换，说明当前文本块无区块引用
                block = '</blockquote>\n' + tmp_block  # 终止区块引用
                self._insideblockquote = False  #　重置标志符
            else:  # 发生了文本替换，说明当前文本块中有区块引用
                block = tmp_block  #　直接替换文本，延续当前区块引用
        else:  # 当前不在区块引用内
            if tmp_block != block:  # 发生了文本替换，说明当前文本块中有区块引用
                block = '<blockquote>\n' + tmp_block  # 开始区块引用
                self._insideblockquote = True
            # 还剩最后一种可能性：不在区块引用内，且未发生文本替换，这种情况不需处理
        return block

    def reset(self):
        """
        重置规则
        """
        self._insideblockquote = False


class EmphasisRule:
    """
    HTML强调 <strong> <em>
    """
    def __init__(self):
        self._strong_1_pattern = re.compile('\*{2}([^*\s]+)\*{2}')
        self._strong_2_pattern = re.compile('_{2}([^_\s]+)_{2}')
        self._em_1_pattern = re.compile('\*([^*\s]+)\*')
        self._em_2_pattern = re.compile('_([^_\s]+)_')
    
    @classmethod
    def _strong_substring(cls, match):
        """
        强调的替换函数
        """
        return '<strong>%s</strong>' % match.group(1)

    @classmethod
    def _em_substring(cls, match):
        """
        强调的替换函数
        """
        return '<em>%s</em>' % match.group(1)   

    def process(self, block):
        """
        按照规则进行处理
        """       
        block = self._strong_1_pattern.sub(self._strong_substring, block)
        block = self._strong_2_pattern.sub(self._strong_substring, block)
        block = self._em_1_pattern.sub(self._em_substring, block)
        block = self._em_2_pattern.sub(self._em_substring, block)
        return block



class LinkRule:
    """
    HTML链接 <a>
    HTML标签
    """
    def __init__(self):
        self._link_1_pattern = re.compile('\[([^\[\]]+)\]\(([^\(\)]+)\)')
        self._link_2_pattern = re.compile('&lt;([a-zA-z]+://[^\s]*)&gt;')
        self._email_pattern = re.compile('&lt;(\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*)&gt;')
        self._html_tag_pattern = re.compile('&lt;(/[a-zA-Z]+?[0-9]*?|[a-zA-Z]+?.*?)&gt;')
        random.seed()

    @classmethod
    def _render_link(cls, address):
        """
        对address进行修饰，替换其中的Markdown特殊字符*和_，以及字符[、]、(和)
        """
        new_address = ''
        for c in address:
            if c == '_':
                new_address += '&lowbar;'
            elif c == '*':
                new_address += '&ast;'
            elif c == '[':
                new_address += '&lbrack;'
            elif c == ']':
                new_address += '&rbrack;'
            elif c == '(':
                new_address += '&lpar;'
            elif c == ')':
                new_address += '&rpar;'
            else:
                new_address += c
        return new_address

    @classmethod
    def _link_1_substring(cls, match):
        """
        链接的替换函数
        """
        linkstring1 = LinkRule._render_link(match.group(1))
        linkstring2 = LinkRule._render_link(match.group(2))
        return '<a href = "%s">%s</a>' % (linkstring2, linkstring1)

    @classmethod
    def _link_2_substring(cls, match):
        """
        链接的替换函数
        """
        linkstring = LinkRule._render_link(match.group(1))
        return '<a href = "%s">%s</a>' % (linkstring, linkstring)

    @classmethod
    def _random_render_email(cls, email):
        """
        Markdown语法要求对email地址进行处理，将其中某些字符改为对应的HTML实体编码或ASCII编码
        如此可避免部分垃圾邮件骚扰
        """
        new_email = ''
        for c in email:
            if c == '@':
                new_email += '&#64;'
            elif c == '.':
                new_email += '&#x2E;'
            elif c == '_':
                new_email += '&lowbar;'
            elif c == '*':
                new_email += '&ast;'
            elif random.random() > 0.2:
                new_email += ('&#x' + binascii.b2a_hex(c.encode()).decode() + ';')
            else:
                new_email += c
        return new_email

    @classmethod
    def _email_substring(cls, match):
        """
        Email链接的替换函数
        """
        email_address = LinkRule._random_render_email(match.group(1)) # 处理email地址
        return '<a href = "&#x6D;&#x61;&#x69;l&#x74;&#x6F;:%s">%s</a>' % (email_address, email_address)

    @classmethod
    def _html_tag_substring(cls, match):
        """
        HTML标签替换函数
        """
        return '<%s>' % match.group(1)

    def process(self, block):
        """
        按照规则进行处理
        """
        block = self._link_1_pattern.sub(self._link_1_substring, block)
        block = self._link_2_pattern.sub(self._link_2_substring, block)
        block = self._email_pattern.sub(self._email_substring, block)
        block = self._html_tag_pattern.sub(self._html_tag_substring, block)
        return block

class ImageRule:
    """
    HTML链接 <a>
    """
    def __init__(self):
        self._img_pattern = re.compile('!\[([^\[\]]+)\]\(([^\(\)]+)\)')

    @classmethod
    def _render_link(cls, address):
        """
        对address进行修饰，替换其中的Markdown特殊字符*和_，以及字符[、]、(和)
        """
        new_address = ''
        for c in address:
            if c == '_':
                new_address += '&lowbar;'
            elif c == '*':
                new_address += '&ast;'
            elif c == '[':
                new_address += '&lbrack;'
            elif c == ']':
                new_address += '&rbrack;'
            elif c == '(':
                new_address += '&lpar;'
            elif c == ')':
                new_address += '&rpar;'
            else:
                new_address += c
        return new_address

    @classmethod
    def _img_substring(cls, match):
        """
        链接的替换函数
        """
        linkstring1 = ImageRule._render_link(match.group(1))
        linkstring2 = ImageRule._render_link(match.group(2))
        return '<img src = "%s" alt = "%s" />' % (linkstring2, linkstring1)

    def process(self, block):
        """
        按照规则进行处理
        """
        block = self._img_pattern.sub(self._img_substring, block)
        return block



class BackslashRule:
    """
    反斜杠逃逸
    """
    def __init__(self):
        self._backslash_pattern = re.compile(r'\\([*+()[\]{}\\_.!#`-])')

    @classmethod
    def _backslash_substring(cls, match):
        """
        反斜杠逃逸替换函数
        """
        if match.group(1) == '_':
            return '&lowbar;'
        elif match.group(1) == '*':
            return '&ast;'
        elif match.group(1) == '+':
            return '&plus;'
        elif match.group(1) == '`':
            return '&grave;'
        elif match.group(1) == '[':
            return '&lbrack;'
        elif match.group(1) == ']':
            return '&rbrack;'
        elif match.group(1) == '(':
            return '&lpar;'
        elif match.group(1) == ')':
            return '&rpar;'
        elif match.group(1) == '{':
            return '&lbrace;'
        elif match.group(1) == '}':
            return '&rbrace;' 
        elif match.group(1) == '\\':
            return '&bsol;'
        elif match.group(1) == '#':
            return '&num;'
        elif match.group(1) == '!':
            return '&excl;'
        elif match.group(1) == '.':
            return '&period;'
        else:    # match.group(1) == '-'
            return '&#45;'

    def process(self, block):
        """
        按照规则进行处理
        """
        block = self._backslash_pattern.sub(self._backslash_substring, block)
        return block
