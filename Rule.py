"""
各种转换规则
"""

import re, random, binascii

inside_code = False  # 判断是否在代码段<code></code>内，这是一个全局标志，会影响所有转换规则的执行


class SpecialChRule:
    """
    HTML特殊字符<, >和&，此规则必须先于其它所有规则执行
    """
    def __init__(self):
        self._leftangle_pattern = re.compile('<')
        self._rightangle_pattern = re.compile('>')
        # 匹配字符&时必须使用否定预测零宽断言（negative lookahead assertion）以避免破坏之前字符<和>的替换结果
        self._ampersand_pattern = re.compile('&(?!#*[0-9a-zA-Z]+;)')

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
        self._inlinecode_pattern = re.compile('`(.+)`')

    @classmethod
    def _inlinecode_substring(cls, match):
        """
        行内代码替换函数
        """
        return '<code>%s</code>' % match.group(1)

    def process(self, block):
        """
        按照规则进行处理
        """
        block = self._inlinecode_pattern.sub(self._inlinecode_substring, block)
        return block



class CodeBlockRule:
    """
    HTML代码块 <pre><code>
    """
    def __init__(self):
        global inside_code 
        self._code_pattern = re.compile('(?<=^)`{3}.*(?=$)', re.M)

    def process(self, block):
        """
        按照规则进行处理
        """
        global inside_code
        # 整个代码区有可能处于同一个block中，因此需要循环两遍分别处理开头和结尾的```
        for i in range(0, 2):  
            if inside_code:  # 当前已经在代码区内
                block = re.sub('_', '&#95;', block)
                block = re.sub('\*', '&#42;', block)
                tmp_block = self._code_pattern.sub('</code></pre>', block, 1)
                if tmp_block != block:  # 发生了替换，终止代码区
                    inside_code = False
                    block = tmp_block
            else:  # 当前不在代码区内
                tmp_block = self._code_pattern.sub('<pre><code>', block, 1)
                if tmp_block != block:  # 发生了替换，开启代码区
                    inside_code = True
                    block = tmp_block
                    block = re.sub('_', '&#95;', block)
                    block = re.sub('\*', '&#42;', block)
        return block

    def reset(self):
        """
        重置规则
        """
        global inside_code
        inside_code = False



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
        return '<h%d>%s</h%d>' % (len(match.group(1)), match.group(2), len(match.group(1)))

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
        if not inside_code:  #　只处理不在代码区块内的文本块，下同
            block = self._atx_pattern.sub(self._atx_substring, block)  # Atx <h1>~<h6>
            block = self._setext_pattern.sub(self._setext_substring, block)  # Setext <h1>、<h2>
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
        if not inside_code:
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
        if not inside_code:
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
        if not inside_code:          
            block = self._strong_1_pattern.sub(self._strong_substring, block)
            block = self._strong_2_pattern.sub(self._strong_substring, block)
            block = self._em_1_pattern.sub(self._em_substring, block)
            block = self._em_2_pattern.sub(self._em_substring, block)
        return block



class LinkRule:
    """
    HTML链接 <a>
    """
    def __init__(self):
        self._link_1_pattern = re.compile('\[([^\[\]]+)\]\(([^\(\)]+)\)')
        self._link_2_pattern = re.compile('&lt;([a-zA-z]+://[^\s]*)&gt;')
        self._email_pattern = re.compile('&lt;(\w+([-+.]\w+)*@\w+([-.]\w+)*\.\w+([-.]\w+)*)&gt;')
        random.seed()

    @classmethod
    def _render_link(cls, address):
        """
        对address进行修饰，替换其中的Markdown特殊字符*和_，以及字符[、]、(和)
        """
        new_address = ''
        for c in address:
            if c == '_':
                new_address += '&#95;'
            elif c == '*':
                new_address += '&#42;'
#            elif c == '[':
#                new_address += '&#91;'
#            elif c == ']':
#                new_address += '&#93;'
#            elif c == '(':
#                new_address += '&#40;'
#            elif c == ')':
#                new_address += '&#41;'
            else:
                new_address += c
        return new_address

    @classmethod
    def _link_1_substring(cls, match):
        """
        链接的替换函数
        """
        s1 = LinkRule._render_link(match.group(1))
        s2 = LinkRule._render_link(match.group(2))
        return '<a href = "%s">%s</a>' % (s2, s1)

    @classmethod
    def _link_2_substring(cls, match):
        """
        链接的替换函数
        """
        s1 = LinkRule._render_link(match.group(1))
        return '<a href = "%s">%s</a>' % (s1, s1)

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
                new_email += '&#95;'
            elif c == '*':
                new_email += '&#42;'
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

    def process(self, block):
        """
        按照规则进行处理
        """
        if not inside_code:
            block = self._link_1_pattern.sub(self._link_1_substring, block)
            block = self._link_2_pattern.sub(self._link_2_substring, block)
            block = self._email_pattern.sub(self._email_substring, block)
        return block



class ParagraphRule:
    """
    HTML段落 <p>
    """
    def __init__(self):
        self._paragraph_pattern = re.compile('(?<=^)(.+)(?=$)', re.S)

    @classmethod
    def _paragraph_substring(cls, match):
        """
        段落的替换函数
        """
        return '<p>%s</p>' % match.group(1)

    def process(self, block):
        """
        按照规则进行处理
        """
        if not inside_code:
            block = self._paragraph_pattern.sub(self._paragraph_substring, block)
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
                new_address += '&#95;'
            elif c == '*':
                new_address += '&#42;'
#            elif c == '[':
#                new_address += '&#91;'
#            elif c == ']':
#                new_address += '&#93;'
#            elif c == '(':
#                new_address += '&#40;'
#            elif c == ')':
#                new_address += '&#41;'
            else:
                new_address += c
        return new_address


    @classmethod
    def _img_substring(cls, match):
        """
        链接的替换函数
        """
        s1 = ImageRule._render_link(match.group(1))
        s2 = ImageRule._render_link(match.group(2))
        return '<img src = "%s" alt = "%s" />' % (s2, s1)


    def process(self, block):
        """
        按照规则进行处理
        """
        if not inside_code:
            block = self._img_pattern.sub(self._img_substring, block)
        return block
