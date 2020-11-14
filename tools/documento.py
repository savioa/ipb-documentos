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


class Documento:
    """Representa um documento, formado por um conjunto de capítulos.

    Attrs:
        capitulos (list[Capitulo]): Conjunto de capítulos do documento.
        titulo (str): Título do documento.
        preambulo (str): Preâmbulo do documento.
    """

    def __init__(self, xml):
        """Inicia uma instância da classe Documento a partir de um objeto XML.

        Args:
            xml (Element): Objeto XML com o conteúdo do documento.
        """

        self.capitulos = []
        self.titulo = xml.attrib['titulo']
        self.preambulo = None

        preambulo = xml.find(NS + 'preambulo')

        if preambulo is not None:
            self.preambulo = preambulo.find(NS + 'texto').text

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

        url_css = 'https://cdn.jsdelivr.net/npm/bulma@0.9.1/css/bulma.min.css'

        css = """
            span[data-lang] { font-style: italic; }
            del { text-decoration: line-through }
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

                        line('h2', 'Índice', klass=f'{CLASSES_SUBTITULO} is-hidden-tablet')
                        with tag('ul', klass='content is-hidden-tablet'):
                            for capitulo in capitulos:
                                with tag('li'):
                                    line('a', capitulo[1], href=f'#{capitulo[0]}')

                        if self.preambulo is not None:
                            with tag('section', id='preambulo', klass='capitulo'):
                                line('h2', 'Preâmbulo', klass=CLASSES_SUBTITULO)
                                line('p', self.preambulo)

                        for capitulo in self.capitulos:
                            capitulo.gerar_html(html)

        return doc

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

        with tag('nav', ('aria-label', 'main navigation'),
                 klass='navbar is-fixed-bottom is-light is-hidden-mobile'):
            with tag('div', klass='navbar-menu'):
                with tag('div', klass='navbar-start'):
                    with tag('div', klass='navbar-item has-dropdown has-dropdown-up is-hoverable'):
                        line('a', 'Índice', href='#', klass='navbar-link')

                        with tag('div', klass='navbar-dropdown'):
                            for capitulo in capitulos:
                                chave = capitulo[0]
                                valor = capitulo[1]
                                line('a', valor, klass='navbar-item', href=f'#{chave}')

                with tag('div', klass='navbar-end'):
                    with tag('div', klass='navbar-item'):
                        with tag('div', klass='field'):
                            with tag('div', klass='control'):
                                doc.stag('input', klass='input', type='text',
                                         placeholder='Vá para um artigo', id='ir')

                    with tag('div', klass='navbar-item'):
                        with tag('label', klass='checkbox'):
                            doc.stag('input', type='checkbox', id='mostrar_versoes')
                            text(' Apresentar versões obsoletas')


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
        versoes_texto (list[VersaoTexto]): Conjunto de versões do texto do item.
        pai (variable): Elemento que contém o item (Artigo, Paragrafo ou Inciso).
    """

    def __init__(self, pai, xml):
        """Inicia uma instância da classe ItemComTextoVersionado a partir de um fragmento de XML.

        Args:
            pai (variable): Elemento que contém o item (Artigo, Paragrafo ou Inciso).
            xml (Element): Fragmento de XML com o conteúdo do item.
        """

        self.versoes_texto = []

        for versao in xml.findall(NS + 'texto'):
            texto = versao.text
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

        return ''

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
        super().__init__(pai, xml)

        alineas = xml.find(NS + 'alineas')

        if alineas is not None:
            for alinea in alineas.findall(NS + 'alinea'):
                self.alineas.append(Alinea(self, alinea))

        incisos = xml.find(NS + 'incisos')

        if incisos is not None:
            for inciso in incisos.findall(NS + 'inciso'):
                self.incisos.append(Inciso(self, inciso))

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
        super().__init__(pai, xml)

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
        super().__init__(pai, xml)

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


class Utilitario:
    """Define métodos e atributos utilitários para o tratamento de um documento."""

    VersaoTexto = namedtuple('VersaoTexto', 'texto instrumento ordem')

    @staticmethod
    def verificar_pontuacao(texto):
        """Verifica a presença de pontuação ao fim de um texto.

        Args:
            texto (str): Texto que deve terminar com pontuação.
        """

        if not texto.endswith(tuple([';', '.', ':'])):
            print(f'{ESCAPE_ALERTA}Alerta{ESCAPE_ENDC}')
            print(f'* Texto sem terminal: {texto}')

    @staticmethod
    def processar_texto(texto, artigo):
        """Processa um texto marcando referências e termos latinos.

        Args:
            texto (str): Texto com referências e termos latinos.
            artigo (Artigo): Artigo que contém o texto.

        Returns:
            str: Texto com referências e termos latinos marcados.
        """

        return Utilitario.marcar_referencias(Utilitario.marcar_termos_latinos(texto), artigo)

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

        regex_artigos = r'arts\. (?:\d{1,3}(?:º)?,)*(?:\d{1,3})(?:º)? e (?:\d{1,3})(?:º)?'
        ocorrencia_artigos = re.search(regex_artigos, texto)

        if ocorrencia_artigos is not None:
            texto_original = ocorrencia_artigos.group(0)
            texto_final = re.sub(r'(\d{1,3})(º)?', r'<a href="#a\1">\1\2</a>', texto_original)
            texto = texto.replace(texto_original, texto_final)

        return re.sub(r'art\. (\d{1,3})(º)?', r'<a href="#a\1">art. \1\2</a>', texto)

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
