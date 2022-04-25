"""Representa um documento da IPB.

Classes:
    Documento
    Capitulo
    Secao
    Artigo
    Paragrafo
    Caput
    Alinea
    Utilitario
"""

import re
import sys
from collections import namedtuple
from operator import attrgetter
import roman
from yattag import Doc

CLASSES_TITULO = 'title is-1 has-text-centered'
CLASSES_SUBTITULO = 'title is-3 has-text-centered'
CLASSES_SECAO = 'title is-5 has-text-centered'

ESCAPE_ALERTA = '\033[33m'
ESCAPE_ERRO = '\033[31m'
ESCAPE_ENDC = '\033[0m'

NS = '{https://savioa.github.io/ipb-documentos}'

REGEX_DOCUMENTOS = r'(__(' \
    r'constituicao.html|estatutos.html|principios_de_liturgia.html|codigo_de_disciplina.html|' \
    r'modelo_de_estatuto_para_igreja_local.html|modelo_de_estatuto_para_o_presbiterio.html)__)?'


class Documento:
    """Representa um documento, formado por um conjunto de capítulos.

    Attrs:
        capitulos (list[Capitulo]): Conjunto de capítulos do documento.
        titulo (str): Título do documento.
        preambulo (str): Preâmbulo do documento.
        blocos_anotacoes_preambulo (list[BlocoAnotacoes]): Conjunto de blocos de anotações do
        preâmbulo do documento.
    """

    def __init__(self, xml):
        """Inicia uma instância da classe Documento a partir de um objeto XML.

        Args:
            xml (Element): Objeto XML com o conteúdo do documento.
        """

        self.capitulos = []
        self.titulo = xml.attrib['titulo']
        self.preambulo = None
        self.blocos_anotacoes_preambulo = []

        preambulo = xml.find(NS + 'preambulo')

        if preambulo is not None:
            self.preambulo = ''

            for fragmento in preambulo.find(NS + 'texto').iter():
                if fragmento.tag.endswith('texto'):
                    self.preambulo += fragmento.text

                if fragmento.tag.endswith('pos'):
                    if fragmento.text != '\n':
                        self.preambulo += f'__{fragmento.attrib["id"]}__{fragmento.tail or ""}'

            for bloco in preambulo.findall(NS + 'anotacoes'):
                self.blocos_anotacoes_preambulo.append(BlocoAnotacoes(bloco))

        for capitulo in xml.findall(NS + 'capitulo'):
            self.capitulos.append(Capitulo(capitulo))

    def gerar_html(self):
        """Gera a materialização do documento como objeto HTML.

        Returns:
            yattag.doc.Doc: Objeto HTML com o documento.
        """

        capitulos = []

        if self.preambulo is not None:
            capitulos.append(('preambulo', 'Preâmbulo'))

        for capitulo in self.capitulos:
            chave = capitulo.obter_id_html()

            if capitulo.ide.isnumeric():
                valor = f'{roman.toRoman(int(capitulo.ide))} - {capitulo.titulo}'
            else:
                valor = capitulo.titulo

            capitulos.append((chave, valor))

        url_css = 'https://cdn.jsdelivr.net/npm/bulma@0.9.3/css/bulma.min.css'

        css = """
            span[data-lang] { font-style: italic; }
            del { text-decoration: line-through }
            .anotacao, .message-body { display: block; }
            .posicao { cursor: help; }
            .paragrafo { margin-left: 1rem!important; }
            .capitulo, .secao, .artigo, .caput, .paragrafo { margin-bottom: 1.5rem; }"""

        doc, tag, text, line = Doc().ttl()
        html = {'doc': doc, 'tag': tag, 'text': text, 'line': line}

        doc.asis('<!doctype html>')

        with tag('html', lang='pt-BR', klass='has-navbar-fixed-bottom'):
            with tag('head'):
                doc.stag('meta', charset='utf-8')
                line('title', self.titulo)
                doc.stag('meta', name='author', content='Igreja Presbiteriana do Brasil')
                doc.stag('meta', name='viewport', content='width=device-width, initial-scale=1')
                doc.stag('link', rel='stylesheet', href=url_css)
                doc.stag('link', rel='shortcut icon', href='favicon.ico', type='image/x-icon')
                doc.stag('link', rel='icon', href='favicon.ico', type='image/x-icon')
                line('style', css)
                line('script', '', src='base.js')

            with tag('body'):
                Documento.gerar_navegacao(html, capitulos)

                with tag('section', klass='section'):
                    with tag('div', klass='container'):
                        line('h1', self.titulo, klass=CLASSES_TITULO)

                        line('h2', 'Índice', klass=CLASSES_SUBTITULO)
                        with tag('ul', klass='content'):
                            for capitulo in capitulos:
                                with tag('li'):
                                    line('a', capitulo[1], href=f'#{capitulo[0]}')

                        if self.preambulo is not None:
                            with tag('section', id='preambulo', klass='capitulo'):
                                line('h2', 'Preâmbulo', klass=CLASSES_SUBTITULO)
                                with tag('p'):
                                    doc.asis(Utilitario.processar_texto(self.preambulo, None))

                                for bloco in self.blocos_anotacoes_preambulo:
                                    bloco.gerar_html(html)

                        for capitulo in self.capitulos:
                            capitulo.gerar_html(html)

                with tag('div', id='modal', klass='modal'):
                    line('div', '', klass='modal-background')
                    line('div', '', klass='modal-content')
                    line('button', '', ('aria-label', 'close'), klass='modal-close is-large')

        return doc.getvalue()

    @staticmethod
    def gerar_navegacao(html, capitulos):
        """Adiciona os elementos de navegação ao objeto HTML.

        Args:
            html (dict): Acessórios para materialização.
            capitulos (list[tuple]): Identificadores e rótulos dos capítulos do documento.
        """

        doc = html['doc']
        tag = html['tag']
        text = html['text']
        line = html['line']

        with tag('nav', ('aria-label', 'main navigation'), ('role', 'navigation'),
                 klass='navbar is-fixed-bottom is-light'):
            with tag('div', klass='navbar-brand'):
                with tag('a', ('aria-label', 'menu'), ('role', 'button'),
                         ('aria-expanded', 'false'), klass='navbar-burger'):
                    line('span', '', ('aria-hidden', 'true'))
                    line('span', '', ('aria-hidden', 'true'))
                    line('span', '', ('aria-hidden', 'true'))

            with tag('div', klass='navbar-menu'):
                with tag('div', klass='navbar-start'):
                    with tag('div', klass='navbar-item has-dropdown has-dropdown-up is-hoverable'):
                        line('a', 'Índice', href='#', klass='navbar-link')

                        with tag('div', klass='navbar-dropdown'):
                            for capitulo in capitulos:
                                chave = capitulo[0]
                                valor = capitulo[1]
                                line('a', valor, klass='navbar-item', href=f'#{chave}')

                    with tag('div', klass='navbar-item has-dropdown has-dropdown-up is-hoverable'):
                        line('a', 'Opções', href='#', klass='navbar-link')

                        with tag('div', klass='navbar-dropdown'):
                            with tag('div', klass='navbar-item'):
                                with tag('label', klass='checkbox'):
                                    doc.stag(
                                        'input',
                                        type='checkbox',
                                        autocomplete='off',
                                        id='mostrar_versoes')
                                    text('Apresentar versões obsoletas')

                            with tag('div', klass='navbar-item'):
                                with tag('label', klass='checkbox'):
                                    doc.stag(
                                        'input',
                                        type='checkbox',
                                        autocomplete='off',
                                        id='mostrar_anotacoes',
                                        checked='checked')
                                    text('Apresentar anotações')

                with tag('div', klass='navbar-end'):
                    with tag('div', klass='navbar-item'):
                        with tag('div', klass='field'):
                            with tag('div', klass='control'):
                                doc.stag('input', klass='input', type='text',
                                        placeholder='Vá para um artigo', id='ir', title="Ctrl + I")


class Capitulo:
    """Representa um capítulo do documento, formado por um conjunto de seções.

    Attrs:
        secoes (list[Secao]): Conjunto de seções do capítulo.
        ide (str): Identificador do capítulo.
        titulo (str): Título do capítulo.
    """

    def __init__(self, xml):
        """Inicia uma instância da classe Capitulo a partir de um fragmento de XML.

        Args:
            xml (Element): Fragmento de XML com o conteúdo do capítulo.
        """

        self.secoes = []
        self.ide = xml.attrib['id']
        self.titulo = xml.attrib['titulo']

        for secao in xml.findall(NS + 'secao'):
            self.secoes.append(Secao(self, secao))

    def gerar_html(self, html):
        """Adiciona a materialização do capítulo ao objeto HTML.

        Args:
            html (dict): Acessórios para materialização.
        """

        tag = html['tag']
        line = html['line']

        with tag('section', id=self.obter_id_html(), klass='capitulo'):
            if self.ide not in ('dg', 'dt'):
                line('h2', f'Capítulo {roman.toRoman(int(self.ide))}', klass=CLASSES_SUBTITULO)

            line('h2', self.titulo, klass=CLASSES_SUBTITULO)

            for secao in self.secoes:
                secao.gerar_html(html)

    def obter_id_html(self):
        """Obtém o identificador do capítulo para uso em link HTML.

        Returns:
            str: Identificador do capítulo.
        """

        return f'c{self.ide}'


class Secao:
    """Representa uma seção de um capítulo, formada por um conjunto de artigos.

    Attrs:
        artigos (list[Artigo]): Conjunto de artigos da seção.
        ide (str): Identificador da seção.
        titulo (str): Título da seção.
        pai (Capitulo): Capítulo que contém a seção.
    """

    def __init__(self, pai, xml):
        """Inicia uma instância da classe Secao a partir de um fragmento de XML.

        Args:
            pai (Capitulo): Capítulo que contém a seção.
            xml (Element): Fragmento de XML com o conteúdo da seção.
        """

        self.artigos = []
        self.ide = int(xml.attrib['id'])
        self.titulo = xml.attrib['titulo'] if 'titulo' in xml.attrib else None
        self.pai = pai

        for artigo in xml.findall(NS + 'artigo'):
            self.artigos.append(Artigo(artigo))

    def gerar_html(self, html):
        """Adiciona a materialização da seção ao objeto HTML.

        Args:
            html (dict): Acessórios para materialização.
        """

        tag = html['tag']
        line = html['line']

        with tag('section', id=self.obter_id_html(), klass='secao'):
            if self.titulo is None:
                titulo = 'Única'
                visibilidade = ' is-sr-only'
            else:
                titulo = f'{self.ide}ª - {self.titulo}'
                visibilidade = ''

            line('h3', f'Seção {titulo}', klass=f'{CLASSES_SECAO}{visibilidade}')

            for artigo in self.artigos:
                artigo.gerar_html(html)

    def obter_id_html(self):
        """Obtém o identificador da seção para uso em link HTML.

        Returns:
            str: Identificador da seção.
        """

        return f'{self.pai.obter_id_html()}_s{self.ide}'


class Artigo:
    """Representa um artigo, formado por um conjunto de parágrafos.

    Attrs:
        paragrafos (list[Paragrafo]): Conjunto de parágrafos do artigo.
        ide (str): Identificador da seção.
    """

    def __init__(self, xml):
        """Inicia uma instância da classe Artigo a partir de um fragmento de XML.

        Args:
            xml (Element): Fragmento de XML com o conteúdo do artigo.
        """

        self.paragrafos = []
        self.ide = int(xml.attrib['id'])

        self.paragrafos.append(Caput(self, xml.find(NS + 'caput')))

        for paragrafo in xml.findall(NS + 'paragrafo'):
            self.paragrafos.append(Paragrafo(self, paragrafo))

    def gerar_html(self, html):
        """Adiciona a materialização do artigo ao objeto HTML.

        Args:
            html (dict): Acessórios para materialização.
        """

        tag = html['tag']

        with tag('div', id=self.obter_id_html(), klass='artigo'):
            for paragrafo in self.paragrafos:
                paragrafo.gerar_html(html)

    def obter_id_html(self):
        """Obtém o identificador do artigo para uso em link HTML.

        Returns:
            str: Identificador do artigo.
        """

        return f'a{self.ide}'


class ItemComTextoVersionado:
    """Representa um item do documento que contém texto versionado (Paragrafo, Inciso ou Alinea).

    Attrs:
        ide (str): Identificador do item.
        versoes_texto (list[VersaoTexto]): Conjunto de versões do texto do item.
        pai (variable): Elemento que contém o item (Artigo, Paragrafo ou Inciso).
    """

    def __init__(self, ide, pai, xml):
        """Inicia uma instância da classe ItemComTextoVersionado a partir de um fragmento de XML.

        Args:
            ide (variable): Identificador do item.
            pai (variable): Elemento que contém o item (Artigo, Paragrafo ou Inciso).
            xml (Element): Fragmento de XML com o conteúdo do item.
        """

        self.ide = ide

        self.versoes_texto = []

        for versao in xml.findall(NS + 'texto'):
            texto = ''

            for fragmento in versao.iter():
                if fragmento.tag.endswith('texto'):
                    texto += fragmento.text

                if fragmento.tag.endswith('pos'):
                    if fragmento.text != '\n':
                        texto += f'__{fragmento.attrib["id"]}__{fragmento.tail or ""}'

                if fragmento.tag.endswith('ref'):
                    documento = Utilitario.substituir_sigla_documento(fragmento.attrib["doc"])

                    texto += f'__{documento}.html__{fragmento.text}{fragmento.tail or ""}'

            instrumento = versao.attrib['instrumento'] if 'instrumento' in versao.attrib else None
            ordem = int(versao.attrib['ordem']) if 'ordem' in versao.attrib else 1

            if any(v.ordem == ordem for v in self.versoes_texto):
                print(f'{ESCAPE_ERRO}Erro{ESCAPE_ENDC}')
                print(f'* Texto com ordem repetida: {texto}')
                sys.exit(1)

            Utilitario.verificar_pontuacao(texto)

            self.versoes_texto.append(Utilitario.VersaoTexto(texto, instrumento, ordem))

        self.versoes_texto = sorted(self.versoes_texto, key=attrgetter('ordem'))

        self.pai = pai

    def gerar_html_versoes(self, html, destacar_rotulo):
        """Adiciona a materialização do item ao objeto HTML.

        Args:
            html (dict): Acessórios para materialização.
            destacar_rotulo (bool): Valor que indica se o rótulo deve ser destacado.
        """

        tag = html['tag']

        numero_versoes = len(self.versoes_texto)
        rotulo = self.obter_rotulo()
        artigo = self.pai

        if not isinstance(artigo, Artigo):
            artigo = artigo.pai

        for indice, versao in enumerate(self.versoes_texto, start=1):
            versao_vigente = indice == numero_versoes

            classes = f"versao{'' if versao_vigente else ' obsoleta is-hidden'}"

            if versao.instrumento is not None:
                with tag('span', ('data-instrumento', versao.instrumento), klass=classes):
                    ItemComTextoVersionado.gerar_versao(
                        html, versao_vigente, rotulo, versao.texto, artigo, destacar_rotulo)
            else:
                with tag('span', klass=classes):
                    ItemComTextoVersionado.gerar_versao(
                        html, versao_vigente, rotulo, versao.texto, artigo, destacar_rotulo)

    def obter_rotulo(self):
        """Obtém o rótulo do item.

        Returns:
            str: Rótulo do item.
        """

        return self.ide

    @staticmethod
    def gerar_versao(html, vigente, rotulo, texto, artigo, destacar_rotulo):
        """Adiciona a materialização da versão do texto de um item ao objeto HTML.

        Args:
            html (dict): Acessórios para materialização.
            vigente (bool): Valor que indica se a versão é vigente.
            rotulo (str): Rótulo do item.
            texto (str): Texto do item na versão.
            artigo (Artigo): Artigo que contém o texto.
            destacar_rotulo (bool): Valor que indica se o rótulo deve ser destacado.
        """

        doc = html['doc']
        tag = html['tag']
        line = html['line']

        if not vigente:
            with tag('del'):
                if destacar_rotulo:
                    line('strong', rotulo)
                    doc.asis(f' {Utilitario.processar_texto(texto, artigo)}')
                else:
                    doc.asis(f'{rotulo} {Utilitario.processar_texto(texto, artigo)}')

            doc.stag('br')
        else:
            if destacar_rotulo:
                line('strong', rotulo)
                doc.asis(f' {Utilitario.processar_texto(texto, artigo)}')
            else:
                doc.asis(f'{rotulo} {Utilitario.processar_texto(texto, artigo)}')


class Paragrafo(ItemComTextoVersionado):
    """Representa um parágrafo de um artigo.

    Attrs:
        ide (str): Identificador da seção.
        alineas (list[Alineas]): Conjunto de alíneas do parágrafo.
        incisos (list[Inciso]): Conjunto de incisos do parágrafo.
        blocos_anotacoes (list[BlocoAnotacoes]): Conjunto de blocos de anotações do parágrafo.
        versoes_texto (list[VersaoTexto]): Conjunto de versões do texto do parágrafo.
        pai (Artigo): Artigo que contém o parágrafo.
    """

    def __init__(self, pai, xml, caput=False):
        """Inicia uma instância da classe Paragrafo a partir de um fragmento de XML.

        Args:
            pai (Artigo): Artigo que contém o parágrafo.
            xml (Element): Fragmento de XML com o conteúdo do parágrafo.
            caput (bool, optional): Valor que indica se o parágrafo é o caput. Padrão: False.
        """

        self.ide = 0 if caput else int(xml.attrib['id'])
        self.alineas = []
        self.incisos = []
        self.blocos_anotacoes = []
        super().__init__(self.ide, pai, xml)

        alineas = xml.find(NS + 'alineas')

        if alineas is not None:
            for alinea in alineas.findall(NS + 'alinea'):
                self.alineas.append(Alinea(self, alinea))

        incisos = xml.find(NS + 'incisos')

        if incisos is not None:
            for inciso in incisos.findall(NS + 'inciso'):
                self.incisos.append(Inciso(self, inciso))

        for bloco in xml.findall(NS + 'anotacoes'):
            self.blocos_anotacoes.append(BlocoAnotacoes(bloco))

    def gerar_html(self, html):
        """Adiciona a materialização do parágrafo ao objeto HTML.

        Args:
            html (dict): Acessórios para materialização.
        """

        tag = html['tag']

        tipo = 'caput' if self.ide == 0 else 'paragrafo'

        with tag('p', id=self.obter_id_html(), klass=f'{tipo} content'):
            self.gerar_html_versoes(html, True)

            for alinea in self.alineas:
                alinea.gerar_html(html)

            for inciso in self.incisos:
                inciso.gerar_html(html)

            for bloco in self.blocos_anotacoes:
                bloco.gerar_html(html)

    def obter_id_html(self):
        """Obtém o identificador do parágrafo para uso em link HTML.

        Returns:
            str: Identificador do parágrafo.
        """

        return f'{self.pai.obter_id_html()}_p{self.ide}'

    def obter_rotulo(self):
        """Obtém o rótulo do parágrafo.

        Returns:
            str: Rótulo do parágrafo.
        """

        if self.ide == 0:
            return f"Art. {self.pai.ide}{'º' if self.pai.ide < 10 else '.'}"

        if len(self.pai.paragrafos) > 2:
            return f'§ {self.ide}º.'

        return 'Parágrafo único.'


class Caput(Paragrafo):
    """Representa o caput de um artigo."""

    def __init__(self, pai, xml):
        """Inicia uma instância da classe Caput a partir de um fragmento de XML.

        Args:
            pai (Artigo): Artigo que contém o caput.
            xml (Element): Fragmento de XML com o conteúdo do caput.
        """

        super().__init__(pai, xml, caput=True)


class Inciso(ItemComTextoVersionado):
    """Representa um inciso de um parágrafo.

    Attrs:
        ide (str): Identificador do inciso.
        alineas (list[Alineas]): Conjunto de alíneas do inciso.
        versoes_texto (list[VersaoTexto]): Conjunto de versões do texto do inciso.
        pai (Paragrafo): Parágrafo que contém o inciso.
    """

    def __init__(self, pai, xml):
        """Inicia uma instância da classe Inciso a partir de um fragmento de XML.

        Args:
            pai (Paragrafo): Parágrafo que contém o inciso.
            xml (Element): Fragmento de XML com o conteúdo do inciso.
        """

        self.ide = int(xml.attrib['id'])
        self.alineas = []
        super().__init__(self.ide, pai, xml)

        alineas = xml.find(NS + 'alineas')

        if alineas is not None:
            for alinea in alineas.findall(NS + 'alinea'):
                self.alineas.append(Alinea(self, alinea))

    def gerar_html(self, html):
        """Adiciona a materialização do inciso ao objeto HTML.

        Args:
            html (dict): Acessórios para materialização.
        """

        doc = html['doc']
        tag = html['tag']

        doc.stag('br')

        with tag('span', id=self.obter_id_html()):
            self.gerar_html_versoes(html, False)

            for alinea in self.alineas:
                alinea.gerar_html(html)

    def obter_id_html(self):
        """Obtém o identificador do inciso para uso em link HTML.

        Returns:
            str: Identificador do inciso.
        """

        return f'{self.pai.obter_id_html()}_i{self.ide}'

    def obter_rotulo(self):
        """Obtém o rótulo do inciso.

        Returns:
            str: Rótulo do inciso.
        """

        return f'{roman.toRoman(self.ide)} -'


class Alinea(ItemComTextoVersionado):
    """Representa uma alínea de um parágrafo.

    Attrs:
        ide (str): Identificador da alínea.
        blocos_anotacoes (list[BlocoAnotacoes]): Conjunto de blocos de anotações da alínea.
        versoes_texto (list[VersaoTexto]): Conjunto de versões do texto da alínea.
        pai (Paragrafo): Parágrafo que contém a alínea.
    """

    def __init__(self, pai, xml):
        """Inicia uma instância da classe Alinea a partir de um fragmento de XML.

        Args:
            pai (Paragrafo): Parágrafo que contém a alínea.
            xml (Element): Fragmento de XML com o conteúdo da alínea.
        """

        self.ide = xml.attrib['id']
        self.blocos_anotacoes = []
        super().__init__(self.ide, pai, xml)

        for bloco in xml.findall(NS + 'anotacoes'):
            self.blocos_anotacoes.append(BlocoAnotacoes(bloco))

    def gerar_html(self, html):
        """Adiciona a materialização da alínea ao objeto HTML.

        Args:
            html (dict): Acessórios para materialização.
        """

        doc = html['doc']
        tag = html['tag']

        doc.stag('br')

        with tag('span', id=self.obter_id_html()):
            self.gerar_html_versoes(html, False)

            for bloco in self.blocos_anotacoes:
                bloco.gerar_html(html)

    def obter_id_html(self):
        """Obtém o identificador da alínea para uso em link HTML.

        Returns:
            str: Identificador da alínea.
        """

        return f'{self.pai.obter_id_html()}_{self.ide}'

    def obter_rotulo(self):
        """Obtém o rótulo da alínea.

        Returns:
            str: Rótulo da alínea.
        """
        return f'{self.ide})'


class BlocoAnotacoes:
    """Representa um bloco de anotações.

    Attrs:
        posicao (str): Identificador da posição do bloco no texto.
        anotacoes (list[Anotacao]): Conjunto de anotações do bloco.
    """

    def __init__(self, xml):
        """Inicia uma instância da classe BlocoAnotacoes a partir de um fragmento de XML.

        Args:
            xml (Element): Fragmento de XML com o bloco de anotações.
        """

        self.posicao = xml.attrib['pos']
        self.anotacoes = []

        for anotacao in xml.findall(NS + 'anotacao'):
            self.anotacoes.append(Anotacao(anotacao))

    def gerar_html(self, html):
        """Adiciona a materialização do bloco de anotações ao objeto HTML.

        Args:
            html (dict): Acessórios para materialização.
        """

        tag = html['tag']

        with tag('span', ('data-posicao', self.posicao), klass='bloco_anotacoes box'):
            for anotacao in self.anotacoes:
                anotacao.gerar_html(html)


class Anotacao:
    """Representa uma anotação.

    Attrs:
        tipo (str): Tipo da anotação.
        texto (str): Texto da anotação.
    """

    def __init__(self, xml):
        """Inicia uma instância da classe Anotacao a partir de um fragmento de XML.

        Args:
            xml (Element): Fragmento de XML com o conteúdo da anotação.
        """

        self.tipo = xml.attrib['tipo']

        texto = ''

        for fragmento in xml.iter():
            if fragmento.tag.endswith('anotacao') and fragmento.text is not None:
                texto += fragmento.text

            if fragmento.tag.endswith('ref'):
                documento = Utilitario.substituir_sigla_documento(fragmento.attrib["doc"])

                texto += f'__{documento}.html__{fragmento.text}{fragmento.tail or ""}'

        Utilitario.verificar_pontuacao(texto)

        self.texto = texto

    def gerar_html(self, html):
        """Adiciona a materialização da anotação ao objeto HTML.

        Args:
            html (dict): Acessórios para materialização.
        """

        doc = html['doc']
        tag = html['tag']

        with tag('span', ('data-tipo', self.tipo), klass='anotacao message'):
            with tag('span', klass='message-body'):
                doc.asis(Utilitario.processar_texto(self.texto, None))


class Utilitario:
    """Define métodos e atributos utilitários para o tratamento de um documento."""

    VersaoTexto = namedtuple('VersaoTexto', 'texto instrumento ordem')

    @staticmethod
    def verificar_pontuacao(texto):
        """Verifica a presença de pontuação ao fim de um texto e de espaços duplos.

        Args:
            texto (str): Texto que deve terminar com pontuação e que não pode conter espaços duplos.
        """

        if not re.match(r'.+(;|\.|:)(__\w__)?$', texto):
            print(f'{ESCAPE_ALERTA}Alerta{ESCAPE_ENDC}')
            print(f'* Texto sem terminal: {texto}')

        if '  ' in texto:
            print(f'{ESCAPE_ALERTA}Alerta{ESCAPE_ENDC}')
            print(f'* Texto com espaços duplos: {texto.replace("  ", "__")}')

    @staticmethod
    def processar_texto(texto, artigo):
        """Processa um texto marcando referências e termos latinos.

        Args:
            texto (str): Texto com referências e termos latinos.
            artigo (Artigo): Artigo que contém o texto.

        Returns:
            str: Texto com referências e termos latinos marcados.
        """

        return Utilitario.marcar_posicoes(
            Utilitario.marcar_referencias(
                Utilitario.marcar_termos_latinos(texto),
                artigo)
        )

    @staticmethod
    def marcar_posicoes(texto):
        """Identifica posições de blocos de anotações e as marca como elementos HTML.

        Args:
            texto (str): Texto com âncoras.

        Returns:
            str: Texto com âncoras marcadas.
        """

        return re.sub(
            r'__([^_]+)__',
            r'<span class="tag posicao">\1</span>',
            texto)

    @staticmethod
    def marcar_referencias(texto, artigo):
        """Identifica referências em um texto e as marca como links HTML.

        Args:
            texto (str): Texto com referências.
            artigo (Artigo): Artigo que contém o texto.

        Returns:
            str: Texto com referências marcadas.
        """

        if 'artigo anterior' in texto:
            texto = re.sub(
                'artigo anterior', f'<a href="#a{artigo.ide - 1}">artigo anterior</a>', texto)

        regex_artigos = re.compile(
            REGEX_DOCUMENTOS +
            r'(a|A)rts\. (?:\d{1,3}(?:º)?, )*(?:\d{1,3})(?:º)? e (?:\d{1,3})(?:º)?')

        ocorrencia_artigos = regex_artigos.search(texto)

        if ocorrencia_artigos is not None:
            texto_original = ocorrencia_artigos.group(0)
            texto_original = texto_original[texto_original.index(
                f'{ocorrencia_artigos.group(3)}rts.'):]

            documento = '' if ocorrencia_artigos.group(2) is None else ocorrencia_artigos.group(2)

            texto_final = re.sub(
                r'(\d{1,3})(º)?',
                rf'<a href="{documento}#a\1">\1\2</a>',
                texto_original)

            texto = texto.replace(ocorrencia_artigos.group(0), texto_final)

        texto = re.sub(
            r'((SC|SC\/IPB|SC-E|CE|CE-SC\/IPB) – \d{4} – DOC. [IVXLCDM]+)',
            r'<strong>\1</strong>',
            texto)

        texto = re.sub(
            REGEX_DOCUMENTOS +
            r'artigos (\d+) a (\d+)',
            r'artigos <a href="\2#a\3">\3</a> a <a href="\2#a\4">\4</a>',
            texto)

        texto = re.sub(
            REGEX_DOCUMENTOS +
            r'(A|a)rts\. (\d+) a (\d+)',
            r'\3rts. <a href="\2#a\4">\4</a> a <a href="\2#a\5">\5</a>',
            texto)

        texto = re.sub(
            REGEX_DOCUMENTOS +
            r'artigo (\d{1,3})(º)?',
            r'<a href="\2#a\3">artigo \3\4</a>',
            texto)

        return re.sub(
            REGEX_DOCUMENTOS +
            r'(a|A)rt\. (\d{1,3})(º)?',
            r'<a href="\2#a\4">\3rt. \4\5</a>',
            texto)

    @staticmethod
    def marcar_termos_latinos(texto):
        """Identifica termos latinos em um texto e os marca para destaque.

        Args:
            texto (str): Texto com termos latinos.

        Returns:
            str: Texto com termos latinos marcados.
        """

        termos = ['ex officio', 'in fine', 'ad referendum', 'quorum', 'ad hoc']
        return re.sub(f"({'|'.join(termos)})", r'<span data-lang="latim">\1</span>', texto)


    @staticmethod
    def substituir_sigla_documento(sigla):
        """Substitui a sigla de um documento pelo seu identificador completo.

        Args:
            sigla (str): Sigla de um documento.

        Returns:
            str: Identificador completo do documento.
        """

        return sigla.replace(
            'ci', 'constituicao').replace(
                'es', 'estatutos').replace(
                    'pl', 'principios_de_liturgia').replace(
                        'cd', 'codigo_de_disciplina').replace(
                            'meil', 'modelo_de_estatuto_para_igreja_local').replace(
                                'mep', 'modelo_de_estatuto_para_o_presbiterio')
