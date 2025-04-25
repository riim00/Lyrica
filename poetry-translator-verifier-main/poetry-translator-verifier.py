import streamlit as st
from deep_translator import GoogleTranslator
import ply.lex as lex
import ply.yacc as yacc
import speech_recognition as sr
import difflib
import re
import openai
import requests
from PIL import Image
from io import BytesIO
import os




# ======================================
# Données des poèmes
# ======================================

french_poems = [
    "Les sanglots longs des violons de l’automne.",
    "Sur mes cahiers d’écolier Sur mon pupitre et les arbres Sur le sable sur la neige J’écris ton nom : Liberté.",
    "Sous le pont Mirabeau coule la Seine Et nos amours, Faut-il qu’il m’en souvienne La joie venait toujours après la peine.",
    "Demain, dès l’aube, à l’heure où blanchit la campagne, Je partirai. Vois-tu, je sais que tu m’attends. J’irai par la forêt, j’irai par la montagne.",
    "Je fais souvent ce rêve étrange et pénétrant D’une femme inconnue, et que j’aime, et qui m’aime.",
    "Il pleure dans mon cœur Comme il pleut sur la ville. Quelle est cette langueur Qui pénètre mon cœur ?",
    "Par les soirs bleus d’été, j’irai dans les sentiers, Picoté par les blés, fouler l’herbe menue.",
    "Heureux qui, comme Ulysse, a fait un beau voyage, Ou comme cestuy-là qui conquit la toison.",
    "Un éclair… puis la nuit ! — Fugitive beauté Dont le regard m’a fait soudainement renaître.",
    "Souvent, pour s’amuser, les hommes d’équipage Prennent des albatros, vastes oiseaux des mers."
]

arabic_poems = [
    "وأنتَ بعيدٌ عن عينيَّ أراكَ قريبا من قلبي كأنك نبضي الذي يتسللُ في شراييني.",
    "إذا المرءُ لم يُدنَسْ مِنَ اللؤمِ عِرضُهُ فكلُّ رِداءٍ يَرتديهِ جميلُ.",
    "قال: السماء كئيبة وتجهما قلت: ابتسم يكفي التجهم في السما.",
    "تعالَ لنسبحَ في ضوء القمر، ونطيرَ في فضاءِ الأحلام.",
    "عيناكِ غابتا نخيلٍ ساعةَ السحَرْ أو شُرفتان راح ينأى عنهما القمرْ.",
    "لا تقف على الأطلال ولا تسأل عن الماضي، فالحياة تمضي وما ذهب، لا يعود.",
    "أراكَ عصيَّ الدمعِ شيمتُكَ الصبرُ أما للهوى نهيٌ عليكَ ولا أمرُ؟",
    "غريبٌ أنا في هذا العالم، غريبٌ كنجمةٍ بعيدة تضيء ولا تنطفئ.",
    "إذا سبَّني نذلٌ تزايدتُ رفعةً وما العيبُ إلّا أن أكونَ مُسابِبَا.",
    "أحبكِ أكثر من كلامي، من صمتي، ومن نظراتي العابرة."
]

english_poems = [
    "Some say the world will end in fire, Some say in ice.",
    "Hope is the thing with feathers - That perches in the soul - And sings the tune without the words - And never stops - at all.",
    "She walks in beauty, like the night Of cloudless climes and starry skies.",
    "All that we see or seem Is but a dream within a dream.",
    "Nature’s first green is gold, Her hardest hue to hold.",
    "Tyger Tyger, burning bright, In the forests of the night.",
    "Do not stand at my grave and weep; I am not there. I do not sleep.",
    "I met a traveller from an antique land Who said: Two vast and trunkless legs of stone Stand in the desert.",
    "There is another sky, Ever serene and fair, And there is another sunshine.",
    "Two roads diverged in a wood, and I— I took the one less traveled by, And that has made all the difference."
]

# ======================================
# Analyseur lexical
# ======================================

tokens = ['WORD', 'COMMA', 'DOT', 'QUESTION', 'EXCLAMATION', 'NEWLINE', 'QUOTE', 'COLON']
t_COMMA = r','
t_DOT = r'\.'
t_QUESTION = r'\?'
t_EXCLAMATION = r'!'
t_QUOTE = r"[’]"
t_COLON = r':'
t_ignore = ' \t'

def t_WORD(t):
    r"[a-zA-ZÀ-ÿ\u0621-\u064A\u0600-\u06FF'-]+"
    return t

def t_NEWLINE(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    return t

def t_error(t):
    st.error(f"Caractère illégal ignoré : '{t.value[0]}'")
    t.lexer.skip(1)

# Construire l'analyseur lexical
lexer = lex.lex()

def analyze_lexical(input_text, poems):
    """Analyse lexicale avec correspondances."""
    lexer.input(input_text)
    tokens = [token.value for token in lexer]

    # Vérifications dans les poèmes
    full_matches = []
    partial_matches = []
    word_matches = {}

    for i, poem in enumerate(poems):
        if input_text.strip() == poem.strip():
            full_matches.append(poem)
        elif input_text.strip() in poem:
            partial_matches.append(poem)
        for word in tokens:
            if word in poem:
                if word not in word_matches:
                    word_matches[word] = []
                word_matches[word].append(poem)

    return tokens, full_matches, partial_matches, word_matches

# ======================================
# Analyse syntaxique et sémantique
# ======================================



# Règles syntaxiques pour les poèmes
def p_start(p):
    '''start : poem'''
    pass

# Règle générale pour identifier un poème
def p_poem(p):
    '''poem : french_poem
            | english_poem
            | arabic_poem'''
    pass

def p_line(p):
    '''line : WORD
            | WORD COMMA line
            | WORD DOT
            | WORD EXCLAMATION
            | WORD QUESTION
            | WORD QUOTE line
            | QUOTE line QUOTE
            | line WORD'''
    pass

def p_french_poem_1(p):
    '''french_poem : WORD WORD WORD WORD WORD WORD WORD DOT'''
    p[0] = "Analyse réussie : 'Les sanglots longs des violons de l’automne.'"

def p_french_poem_2(p):
    '''french_poem : WORD WORD WORD WORD WORD WORD WORD WORD WORD WORD WORD WORD WORD COLON WORD DOT'''
    p[0] = "Analyse réussie : 'Sur mes cahiers d’écolier... J’écris ton nom : Liberté.'"

def p_french_poem_3(p):
    '''french_poem : WORD WORD WORD WORD WORD WORD WORD WORD WORD WORD WORD WORD WORD WORD WORD WORD WORD WORD WORD WORD DOT'''
    p[0] = "Analyse réussie : 'Sous le pont Mirabeau coule la Seine... après la peine.'"

def p_french_poem_4(p):
    '''french_poem : WORD COMMA WORD WORD COMMA WORD WORD WORD WORD WORD WORD WORD COMMA WORD WORD DOT WORD DASH WORD COMMA WORD WORD WORD WORD WORD WORD WORD WORD DOT'''
    p[0] = "Analyse réussie : 'Demain, dès l’aube... j’irai par la montagne.'"

def p_french_poem_5(p):
    '''french_poem : WORD WORD WORD WORD WORD WORD WORD WORD WORD WORD WORD COMMA WORD WORD WORD WORD COMMA WORD WORD WORD WORD DOT'''
    p[0] = "Analyse réussie : 'Je fais souvent ce rêve... et qui m’aime.'"

def p_french_poem_6(p):
    '''french_poem : WORD WORD WORD WORD WORD WORD WORD WORD WORD DOT WORD WORD WORD WORD WORD WORD WORD WORD WORD WORD WORD QUESTION'''
    p[0] = "Analyse réussie : 'Il pleure dans mon cœur... Qui pénètre mon cœur ?'"

def p_french_poem_7(p):
    '''french_poem : WORD WORD WORD WORD WORD WORD WORD WORD WORD WORD WORD WORD COMMA WORD WORD WORD WORD WORD COMMA WORD WORD WORD WORD WORD WORD DOT'''
    p[0] = "Analyse réussie : 'Par les soirs bleus... fouler l’herbe menue.'"

def p_french_poem_8(p):
    '''french_poem : WORD WORD COMMA WORD WORD COMMA WORD WORD WORD WORD WORD COMMA WORD WORD WORD WORD WORD WORD WORD WORD DOT'''
    p[0] = "Analyse réussie : 'Heureux qui, comme Ulysse... conquit la toison.'"

def p_french_poem_9(p):
    '''french_poem : WORD WORD WORD WORD WORD EXCLAMATION DASH WORD WORD WORD WORD WORD WORD WORD WORD WORD WORD WORD WORD DOT'''
    p[0] = "Analyse réussie : 'Un éclair… puis la nuit !... renaître.'"

def p_french_poem_10(p):
    '''french_poem : WORD COMMA WORD WORD WORD COMMA WORD WORD WORD WORD WORD WORD WORD COMMA WORD WORD WORD WORD WORD WORD WORD DOT'''
    p[0] = "Analyse réussie : 'Souvent, pour s’amuser... vastes oiseaux des mers.'"




def p_english_poem_1(p):
    '''english_poem : WORD WORD WORD WORD WORD WORD COMMA WORD WORD WORD DOT'''
    p[0] = "Analyse réussie : 'Some say the world will end in fire, Some say in ice.'"

def p_english_poem_2(p):
    '''english_poem : WORD WORD WORD WORD WORD DASH WORD WORD WORD WORD WORD DASH WORD WORD WORD WORD WORD WORD WORD DASH WORD WORD'''
    p[0] = "Analyse réussie : 'Hope is the thing with feathers - That perches in the soul - And never stops - at all.'"

def p_english_poem_3(p):
    '''english_poem : WORD WORD WORD WORD COMMA WORD WORD WORD WORD WORD WORD WORD WORD WORD DOT'''
    p[0] = "Analyse réussie : 'She walks in beauty, like the night Of cloudless climes and starry skies.'"

def p_english_poem_4(p):
    '''english_poem : WORD WORD WORD WORD WORD WORD WORD WORD WORD WORD WORD WORD DOT'''
    p[0] = "Analyse réussie : 'All that we see or seem Is but a dream within a dream.'"

def p_english_poem_5(p):
    '''english_poem : WORD WORD WORD WORD WORD COMMA WORD WORD WORD WORD DOT'''
    p[0] = "Analyse réussie : 'Nature’s first green is gold, Her hardest hue to hold.'"

def p_english_poem_6(p):
    '''english_poem : WORD WORD COMMA WORD WORD COMMA WORD WORD WORD WORD WORD DOT'''
    p[0] = "Analyse réussie : 'Tyger Tyger, burning bright, In the forests of the night.'"

def p_english_poem_7(p):
    '''english_poem : WORD WORD WORD WORD WORD WORD WORD WORD WORD SEMICOLON WORD WORD WORD WORD DOT WORD WORD WORD WORD DOT'''
    p[0] = "Analyse réussie : 'Do not stand at my grave and weep; I am not there. I do not sleep.'"

def p_english_poem_8(p):
    '''english_poem : WORD WORD WORD WORD WORD WORD WORD WORD WORD COLON WORD WORD WORD WORD WORD WORD WORD WORD WORD WORD WORD DOT'''
    p[0] = "Analyse réussie : 'I met a traveller from an antique land Who said: Two vast and trunkless legs of stone Stand in the desert.'"

def p_english_poem_9(p):
    '''english_poem : WORD WORD WORD WORD COMMA WORD WORD WORD WORD COMMA WORD WORD WORD WORD WORD DOT'''
    p[0] = "Analyse réussie : 'There is another sky, Ever serene and fair, And there is another sunshine.'"

def p_english_poem_10(p):
    '''english_poem : WORD WORD WORD WORD WORD COMMA WORD WORD DASH WORD DASH WORD WORD WORD WORD WORD WORD COMMA WORD WORD WORD WORD WORD WORD WORD WORD WORD DOT'''
    p[0] = "Analyse réussie : 'Two roads diverged in a wood, and I— I took the one less traveled by, And that has made all the difference.'"




def p_arabic_poem_1(p):
    '''arabic_poem : WORD WORD WORD WORD WORD WORD WORD WORD WORD WORD WORD WORD WORD WORD WORD DOT'''
    p[0] = "Analyse réussie : 'وأنتَ بعيدٌ عن عينيَّ أراكَ قريبا من قلبي كأنك نبضي الذي يتسللُ في شراييني.'"

def p_arabic_poem_2(p):
    '''arabic_poem : WORD WORD WORD WORD WORD WORD WORD WORD WORD WORD WORD DOT'''
    p[0] = "Analyse réussie : 'إذا المرءُ لم يُدنَسْ مِنَ اللؤمِ عِرضُهُ فكلُّ رِداءٍ يَرتديهِ جميلُ.'"

def p_arabic_poem_3(p):
    '''arabic_poem : WORD COLON WORD WORD WORD WORD WORD COLON WORD WORD WORD WORD WORD WORD DOT'''
    p[0] = "Analyse réussie : 'قال: السماء كئيبة وتجهما قلت: ابتسم يكفي التجهم في السما.'"

def p_arabic_poem_4(p):
    '''arabic_poem : WORD WORD WORD WORD WORD WORD COMMA WORD WORD WORD WORD WORD DOT'''
    p[0] = "Analyse réussie : 'تعالَ لنسبحَ في ضوء القمر، ونطيرَ في فضاءِ الأحلام.'"

def p_arabic_poem_5(p):
    '''arabic_poem : WORD WORD WORD WORD WORD WORD WORD WORD WORD WORD WORD WORD WORD DOT'''
    p[0] = "Analyse réussie : 'عيناكِ غابتا نخيلٍ ساعةَ السحَرْ أو شُرفتان راح ينأى عنهما القمرْ.'"

def p_arabic_poem_6(p):
    '''arabic_poem : WORD WORD WORD WORD WORD WORD WORD WORD WORD COMMA WORD WORD WORD WORD WORD COMMA WORD WORD DOT'''
    p[0] = "Analyse réussie : 'لا تقف على الأطلال ولا تسأل عن الماضي، فالحياة تمضي وما ذهب، لا يعود.'"

def p_arabic_poem_7(p):
    '''arabic_poem : WORD WORD WORD WORD WORD WORD WORD WORD WORD WORD WORD QUESTION'''
    p[0] = "Analyse réussie : 'أراكَ عصيَّ الدمعِ شيمتُكَ الصبرُ أما للهوى نهيٌ عليكَ ولا أمرُ؟'"

def p_arabic_poem_8(p):
    '''arabic_poem : WORD WORD WORD WORD WORD COMMA WORD WORD WORD WORD WORD WORD WORD WORD WORD DOT'''
    p[0] = "Analyse réussie : 'غريبٌ أنا في هذا العالم، غريبٌ كنجمةٍ بعيدة تضيء ولا تنطفئ.'"

def p_arabic_poem_9(p):
    '''arabic_poem : WORD WORD WORD WORD WORD WORD WORD WORD WORD WORD WORD WORD DOT'''
    p[0] = "Analyse réussie : 'إذا سبَّني نذلٌ تزايدتُ رفعةً وما العيبُ إلّا أن أكونَ مُسابِبَا.'"

def p_arabic_poem_10(p):
    '''arabic_poem : WORD WORD WORD WORD WORD COMMA WORD WORD COMMA WORD WORD WORD WORD DOT'''
    p[0] = "Analyse réussie : 'أحبكِ أكثر من كلامي، من صمتي، ومن نظراتي العابرة.'"




def p_error(p):
    """
    Gestion des erreurs syntaxiques.
    """
    if p:
        raise Exception(f"Erreur syntaxique au token : {p.value}")
    else:
        raise Exception("Erreur syntaxique : fin de fichier inattendue.")
    

    
def p_error_french(p):
    """
    Gestion des erreurs syntaxiques pour les poèmes français.
    """
    if p:
        raise Exception(f"Erreur syntaxique au token : {p.value}")
    else:
        raise Exception("Erreur syntaxique : fin de fichier inattendue.")
    

    
def p_error_english(p):
    """
    Gestion des erreurs syntaxiques pour les poèmes anglais.
    """
    if p:
        raise Exception(f"Erreur syntaxique au token : {p.value}")
    else:
        raise Exception("Erreur syntaxique : fin de fichier inattendue.")
    

def p_error_arabic(p):
    """
    Gestion des erreurs syntaxiques pour les poèmes arabes.
    """
    if p:
        raise Exception(f"Erreur syntaxique au token : {p.value}")
    else:
        raise Exception("Erreur syntaxique : fin de fichier inattendue.")



def analyze_semantics(input_text, detected_lang):
    """
    Analyse sémantique d'un poème pour détecter des anomalies.
    """
    observations = []

    # Vérification de la longueur minimale
    if len(input_text.split()) < 3:
        observations.append("Le texte semble trop court pour être un poème.")

    # Vérification des majuscules (sauf pour l'arabe)
    if detected_lang != "ar" and input_text == input_text.upper():
        observations.append("Le texte est entièrement en majuscules, ce qui peut être incohérent pour un poème.")

    # Vérification des virgules consécutives
    if re.search(r',,{1,}', input_text):
        observations.append("Le texte contient des virgules consécutives, ce qui est incorrect.")

    # Vérification des points consécutifs
    if re.search(r'\.{2,}', input_text):
        observations.append("Le texte contient des points consécutifs, ce qui est incorrect.")

    # Vérification des points d'exclamation consécutifs
    if re.search(r'!{2,}', input_text):
        observations.append("Le texte contient des points d'exclamation consécutifs, ce qui est incorrect.")

    # Vérification des points d'interrogation consécutifs
    if re.search(r'\?{2,}', input_text):
        observations.append("Le texte contient des points d'interrogation consécutifs, ce qui est incorrect.")

    # Vérification des lignes vides
    lines = input_text.split('\n')
    for i, line in enumerate(lines):
        if len(line.strip()) == 0 and i != len(lines) - 1:  # Ignorer la dernière ligne vide
            observations.append("Une ou plusieurs lignes sont vides, ce qui peut indiquer une incohérence.")

    # Vérification des lignes sans mots
    for line in lines:
        words = [word for word in line.split() if word.isalpha()]
        if len(words) == 0 and len(line.strip()) > 0:
            observations.append(f"La ligne suivante ne contient aucun mot : \"{line.strip()}\"")

    return observations



# ======================================
# Traduction
# ======================================

def translate_line(line, source_lang, target_lang):
    try:
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        return translator.translate(line)
    except Exception as e:
        return f"Erreur de traduction: {e}"

def translate_poem(poem_lines, source_lang, target_lang):
    return [translate_line(line, source_lang, target_lang) for line in poem_lines]


# ======================================
# Reconnaissance vocale et analyse
# ======================================

def transcribe_audio():
    """
    Reconnaît un poème récité via le microphone et le transcrit.
    :return: Texte transcrit ou message d'erreur.
    """
    recognizer = sr.Recognizer()
    try:
        with sr.Microphone() as source:
            st.info("Veuillez réciter votre poème...")
            recognizer.adjust_for_ambient_noise(source)  # Ajuste pour le bruit ambiant
            audio = recognizer.listen(source)
            st.info("Transcription en cours...")
            transcription = recognizer.recognize_google(audio, language="fr-FR")
            return transcription
    except sr.UnknownValueError:
        return "Erreur : Impossible de comprendre l'audio."
    except sr.RequestError as e:
        return f"Erreur de reconnaissance vocale : {e}"


def compare_transcription_with_poems(transcribed_text, known_poems):
    """
    Compare une transcription avec des poèmes connus pour trouver des correspondances.
    :param transcribed_text: Texte transcrit via reconnaissance vocale.
    :param known_poems: Liste des poèmes connus.
    :return: Liste de correspondances avec leurs scores.
    """
    matches = []
    for poem in known_poems:
        similarity = difflib.SequenceMatcher(None, transcribed_text, poem).ratio()
        if similarity > 0.6:  # Seuil de similarité
            matches.append((poem, similarity))
    matches.sort(key=lambda x: x[1], reverse=True)  # Trie par score décroissant
    return matches


# ======================================
# Analyse stylistique
# ======================================

def count_syllables(line):
    """
    Compte le nombre de syllabes dans une ligne.
    """
    vowels = "aeiouyAEIOUYéèêëàâîïôùûç"
    # Identifier les groupes de voyelles
    syllable_groups = re.findall(r"[aeiouyAEIOUYéèêëàâîïôùûç]+", line)
    return len(syllable_groups)



def detect_rhyme_scheme(lines):
    """
    Analyse le schéma des rimes d'un poème.
    """
    rhymes = {}
    scheme = []
    rhyme_index = 0

    for line in lines:
        if line.strip():
            # Extraire le dernier mot
            last_word = line.strip().split()[-1].lower()
            # Conserver une portion significative des sons de rime
            rhyme = re.sub(r"[^a-zA-Zéèêëàâîïôùûç]", "", last_word[-4:])  # Ajusté à 4 lettres

            if rhyme not in rhymes:
                rhyme_index += 1
                rhymes[rhyme] = chr(64 + rhyme_index)  # A, B, C...
            scheme.append(rhymes[rhyme])
        else:
            scheme.append(" ")  # Ligne vide

    return "".join(scheme)



def detect_figures_of_speech(line):
    """
    Détecte des figures de style dans une ligne.
    """
    figures = []

    # Allitération : répétition des sons
    if re.search(r"(.)\1{2,}", line):
        figures.append("Allitération")

    # Métaphore ou comparaison : mots-clés potentiels
    if "comme" in line or "tel" in line:
        figures.append("Comparaison")

    # Anaphore : répétition de début
    words = line.split()
    if len(words) > 1 and words[0] == words[1]:
        figures.append("Anaphore")

    return figures


def analyze_style(poem):
    """
    Analyse stylistique d'un poème.
    """
    lines = poem.strip().split("\n")
    style_report = {"syllables_per_line": [], "rhyme_scheme": "", "figures": []}

    # Analyse ligne par ligne
    for line in lines:
        syllable_count = count_syllables(line)
        style_report["syllables_per_line"].append(syllable_count)
        figures = detect_figures_of_speech(line)
        style_report["figures"].extend(figures)

    # Schéma de rimes
    style_report["rhyme_scheme"] = detect_rhyme_scheme(lines)

    return style_report

def generate_image_description(poem):
    """
    Génère une description textuelle pour l'image à partir d'un poème.
    """
    lines = poem.strip().split("\n")
    summary = " ".join(lines[:2])  # Utilise les deux premières lignes pour résumer
    description = f"An artistic representation of the following poem: {summary}"
    return description


def load_images_for_poem_by_language(poem_number, language_code):
    """
    Charge les images pour un poème spécifique et une langue donnée depuis la structure des répertoires.
    """
    # Mapper les langues aux dossiers
    language_mapping = {
       "ar": r"C:\ImagesPoems\Poems_ar",
       "fr": r"C:\ImagesPoems\Poems_fr",
       "en": r"C:\ImagesPoems\Poems_en"
    }


    folder_suffix = language_mapping.get(language_code, "")
    folder_path = os.path.join(folder_suffix, f"Poem{poem_number}")

    if not os.path.exists(folder_path):
        return []  # Retourner une liste vide si le dossier n'existe pas

    # Charger les images disponibles dans le dossier sans afficher les fichiers
    images = [
        os.path.join(folder_path, filename)
        for filename in sorted(os.listdir(folder_path))
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))
    ]
    return images




def show_image_for_poem_by_language(poem_number, language_code):
    """
    Affiche une image pour un poème spécifique et une langue donnée avec une logique de rotation.
    """
    if f"poem_{language_code}_{poem_number}_index" not in st.session_state:
        st.session_state[f"poem_{language_code}_{poem_number}_index"] = 0

    images = load_images_for_poem_by_language(poem_number, language_code)
    if not images:
        st.error(f"Aucune image trouvée pour Poem{poem_number} dans la langue {language_code}.")
        return

    # Afficher uniquement l'image correspondante
    index = st.session_state[f"poem_{language_code}_{poem_number}_index"]
    image_path = images[index % len(images)]  # Rotation des images
    image = Image.open(image_path)
    st.image(image, caption=f"Image pour Poem{poem_number} ({language_code})", use_column_width=True)

    # Incrémenter l'index pour la prochaine exécution
    st.session_state[f"poem_{language_code}_{poem_number}_index"] += 1


from langdetect import detect, DetectorFactory
DetectorFactory.seed = 0  # Assure des résultats cohérents

def detect_language(input_text):
    """
    Détecte la langue d'un texte en utilisant langdetect.
    """
    try:
        detected_lang = detect(input_text)
        lang_mapping = {
            "fr": "fr",
            "ar": "ar",
            "en": "en"
        }
        return lang_mapping.get(detected_lang, "unknown")
    except Exception as e:
        return "unknown"


def identify_poem(input_text, language):
    """
    Identifie le poème correspondant à l'entrée.
    """
    poems_dict = {"fr": french_poems, "ar": arabic_poems, "en": english_poems}
    poems = poems_dict.get(language, [])
    
    for i, poem in enumerate(poems):
        if difflib.SequenceMatcher(None, input_text.strip(), poem.strip()).ratio() > 0.8:
            return i + 1, poem  # Retourne l'index et le poème correspondant
    return None, None


def detect_errors(input_text, reference_poem):
    """
    Détecte les erreurs (mots ou caractères manquants) dans le texte saisi par rapport au poème de référence.
    """
    errors = []
    
    input_words = input_text.strip().split()
    reference_words = reference_poem.strip().split()
    
    # Vérification mot par mot
    for i, word in enumerate(reference_words):
        if i >= len(input_words) or input_words[i] != word:
            previous_word = reference_words[i - 1] if i > 0 else None
            next_word = reference_words[i + 1] if i < len(reference_words) - 1 else None
            errors.append({
                "type": "word",
                "missing_word": word,
                "position": i,
                "before": previous_word,
                "after": next_word
            })
    
    # Vérification des caractères manquants pour les mots correspondants
    for i, (input_word, ref_word) in enumerate(zip(input_words, reference_words)):
        if input_word != ref_word:
            for j, (input_char, ref_char) in enumerate(zip(input_word, ref_word)):
                if input_char != ref_char:
                    errors.append({
                        "type": "character",
                        "missing_character": ref_char,
                        "word_position": i,
                        "char_position": j
                    })
    
    # Vérification du caractère final manquant
    if reference_poem.endswith('.') and not input_text.endswith('.'):
        errors.append({
            "type": "character",
            "missing_character": '.',
            "word_position": len(reference_words) - 1,
            "after_word": reference_words[-1]
        })
    
    return errors

def detect_syntax_errors(input_text, reference_poem):
    """
    Détecte les erreurs syntaxiques dans un texte en le comparant au poème de référence.
    :param input_text: Texte saisi par l'utilisateur.
    :param reference_poem: Poème de référence.
    :return: Liste des erreurs détectées.
    """
    errors = []
    
    # Séparer les mots dans le texte d'entrée et le poème de référence
    input_words = input_text.strip().split()
    reference_words = reference_poem.strip().split()
    
    # Vérification mot par mot
    for i, word in enumerate(reference_words):
        if i >= len(input_words):  # Mot manquant
            errors.append({
                "type": "missing_word",
                "missing_word": word,
                "position": i
            })
        elif input_words[i] != word:  # Mot incorrect
            errors.append({
                "type": "incorrect_word",
                "expected_word": word,
                "actual_word": input_words[i],
                "position": i
            })

    # Vérification des mots supplémentaires dans le texte d'entrée
    if len(input_words) > len(reference_words):
        for i in range(len(reference_words), len(input_words)):
            errors.append({
                "type": "extra_word",
                "extra_word": input_words[i],
                "position": i
            })

    return errors





def analyze_syntax(input_text, language):
    """
    Analyse syntaxique du texte en fonction des poèmes de la langue sélectionnée.
    Vérifie également si la langue du texte saisi correspond à la langue choisie.
    :param input_text: Texte saisi par l'utilisateur.
    :param language: Langue sélectionnée (fr, ar, en).
    :return: Résultat d'analyse syntaxique et erreurs détectées.
    """
    detected_language = detect_language(input_text)  # Détection automatique de la langue
    
    if detected_language != language:
        return (
            f"La langue du texte saisi ne correspond pas à la langue sélectionnée. "
            f"Langue détectée : {detected_language}. Langue attendue : {language}.",
            []
        )

    poems_dict = {"fr": french_poems, "ar": arabic_poems, "en": english_poems}
    poems = poems_dict.get(language, [])

    # Identifier le poème correspondant
    best_match = None
    highest_similarity = 0
    for poem in poems:
        similarity = difflib.SequenceMatcher(None, input_text.strip(), poem.strip()).ratio()
        if similarity > highest_similarity:
            highest_similarity = similarity
            best_match = poem

    if best_match is None:
        return "Aucun poème correspondant trouvé.", []

    # Détecter les erreurs dans le poème
    errors = detect_syntax_errors(input_text, best_match)

    return f"Poème correspondant détecté : {best_match}", errors





# ======================================
# Application Streamlit
# ======================================


def home_page():
    st.title("🎼 Bienvenue sur Lyrica Translate 🌐")
    st.markdown("""
    ## 🎵 **Compilateur-Traducteur Multilingue Avancé**  
    Découvrez **Lyrica Translate**, une application révolutionnaire qui transcende les frontières linguistiques et artistiques pour donner vie à vos poèmes 🎶.  

    ### 🌟 **Fonctionnalités principales**  
    - **Analyse Lexicale & Syntaxique** 🕵️‍♂️ : Identifiez les mots, les erreurs de syntaxe, et validez la structure de vos poèmes dans les langues **français 🇫🇷, arabe 🇸🇦, et anglais 🇬🇧**.  
    - **Analyse Sémantique** 📖 : Détectez les anomalies contextuelles et améliorez la cohérence de vos écrits.  
    - **Traduction Multilingue** 🌐 : Traduisez vos poèmes entre **français**, **arabe**, et **anglais** avec une précision exceptionnelle.  
    - **Détection d'Erreurs Linguistiques** ⚠️ : Trouvez les mots ou caractères manquants, les ajouts superflus, et corrigez vos textes avec facilité.  
    - **Analyse Stylistique** ✨ : Explorez les schémas de rimes, détectez les figures de style, et améliorez vos créations.  
    - **Récitation Vocale** 🎙️ : Récitez vos poèmes directement au compilateur pour les analyser et les comparer aux poèmes connus.  
    - **Détection Automatique de la Langue** 🌍 : Vérifiez si la langue saisie correspond à la langue attendue pour un traitement précis.  
    - **Génération d'Images Artistiques** 🖼️ : Transformez vos poèmes en images uniques et captivantes grâce à une technologie avancée.  

    ### 💡 **Pourquoi choisir Lyrica Translate ?**  
    - **Intuitif & Innovant** : Une interface conviviale et facile à utiliser, même pour les novices.  
    - **Polyvalent & Puissant** : Parfait pour les poètes, les linguistes, et les amateurs de langues.  
    - **Technologie de Pointe** : Intègre des outils comme Lex & Yacc pour des analyses approfondies.  

    ### 🎨 **Transformez vos poèmes en œuvres d'art**  
    Avec notre fonctionnalité de génération d'images, visualisez vos poèmes sous un nouvel angle artistique. Exprimez-vous non seulement avec des mots, mais aussi avec des images !

    ---
    **Prêt à explorer ?** Sélectionnez une option dans la barre latérale pour commencer votre voyage poétique ! ✨
    """)



def compilateur_page():
    st.title("Compilateur de Lyrica Translate 🎼🌐")

    # Mapping des langues
    language_mapping = {
        "Français": "fr",
        "Arabe": "ar",
        "Anglais": "en"
    }

    # Sélection de la langue et de la langue cible pour la traduction
    language = st.selectbox("Langue du poème :", ["Français", "Arabe", "Anglais"])
    target_lang = st.selectbox("Traduire vers :", ["Français", "Arabe", "Anglais"])
    source_lang_code = language_mapping.get(language)
    target_lang_code = language_mapping.get(target_lang)
    poems = {"Français": french_poems, "Arabe": arabic_poems, "Anglais": english_poems}[language]

    # Zone de texte pour saisir le poème
    input_text = st.text_area("Écrivez ou collez votre texte ici :", height=200)

     # **Détection de la langue avant toute analyse**
    if input_text.strip():  # Vérifiez que l'utilisateur a saisi un texte
        detected_lang = detect_language(input_text)
        if detected_lang != source_lang_code:
            st.error(f"La langue du texte saisi ne correspond pas à la langue sélectionnée. Langue détectée : {detected_lang}. Langue attendue : {source_lang_code}.")
            return  # Arrêtez l'exécution si les langues ne correspondent pas

    # Analyse et vérification
    if st.button("Analyser et Vérifier"):
        if not input_text.strip():
            st.error("Veuillez entrer du texte avant de continuer.")
        else:
            st.subheader("Analyse Lexicale")
            tokens, full_matches, partial_matches, word_matches = analyze_lexical(input_text, poems)
            st.write(f"Tokens extraits : {tokens}")

            if full_matches:
                st.success(f"Correspondance complète trouvée dans : {full_matches}")
            if partial_matches:
                st.info(f"Correspondance partielle trouvée dans : {partial_matches}")

            st.subheader("Analyse Syntaxique")
            syntax_result, syntax_errors = analyze_syntax(input_text, source_lang_code)

            # Affichage des résultats
            if "Langue détectée" in syntax_result:  # Vérifier si une langue incorrecte est détectée
                st.error(syntax_result)
            else:
                st.write(syntax_result)

                if syntax_errors:
                    st.error("Erreurs détectées :")
                    for error in syntax_errors:
                        if error["type"] == "missing_word":
                            st.warning(f"Mot manquant : '{error['missing_word']}' à la position {error['position']}.")
                        elif error["type"] == "extra_word":
                            st.warning(f"Mot supplémentaire : '{error['extra_word']}' à la position {error['position']}.")
                        elif error["type"] == "incorrect_word":
                            st.warning(f"Mot incorrect à la position {error['position']}: attendu '{error['expected_word']}', trouvé '{error['actual_word']}'.")
                        elif error["type"] == "missing_character":
                            st.warning(f"Caractère manquant : '{error['missing_char']}' dans le mot à la position {error['word_position']}, caractère {error['char_position']}.")
                        elif error["type"] == "extra_character":
                            st.warning(f"Caractère supplémentaire : '{error['extra_char']}' dans le mot à la position {error['word_position']}, caractère {error['char_position']}.")
                        elif error["type"] == "character_error":
                            st.warning(f"Caractère incorrect dans le mot à la position {error['word_position']}, caractère {error['char_position']}: attendu '{error['expected_char']}', trouvé '{error['actual_char']}'.")
                else:
                    st.success("Aucune erreur détectée.")

            st.subheader("Analyse Sémantique")
            detected_lang = detect_language(input_text)
            semantic_results = analyze_semantics(input_text, detected_lang)
            if semantic_results:
                for obs in semantic_results:
                    st.warning(obs)
            else:
                st.success("Aucune anomalie sémantique détectée.")

            st.subheader("Analyse Stylistique")
            style_report = analyze_style(input_text)
            st.write("**Syllabes par ligne :**", style_report["syllables_per_line"])
            st.write("**Schéma de rimes :**", style_report["rhyme_scheme"])
            st.write("**Figures de style détectées :**", style_report["figures"])

            st.subheader("Traduction")
            poem_lines = input_text.split('\n')
            translated_poem = translate_poem(poem_lines, source_lang_code, target_lang_code)
            st.text_area("Poème traduit :", "\n".join(translated_poem), height=200)
     

    # Fonctionnalité de récitation vocale
    st.subheader("Récitation Vocale")
    if st.button("Réciter un poème"):
        transcribed_text = transcribe_audio()
        st.subheader("Texte Transcrit")
        if "Erreur" in transcribed_text:
            st.error(transcribed_text)
        else:
            st.success("Texte transcrit avec succès :")
            st.text_area("Texte transcrit :", transcribed_text, height=100)

            # Comparer avec les poèmes connus
            st.subheader("Comparaison avec des Poèmes Connus")
            matches = compare_transcription_with_poems(transcribed_text, poems)

            if matches:
                for poem, similarity in matches:
                    st.info(f"Correspondance trouvée ({similarity * 100:.2f}% de similarité) :\n{poem}")
            else:
                st.warning("Aucune correspondance trouvée.")

    # Affichage des images associées
    if st.button("Afficher une Image pour le Poème"):
        matched_poem_index = None
        for i, poem in enumerate(poems):
            if input_text.strip() == poem.strip():
                matched_poem_index = i + 1
                break

        if matched_poem_index:
            st.success(f"Poème reconnu : Poem{matched_poem_index}")
            show_image_for_poem_by_language(matched_poem_index, source_lang_code)
        else:
            st.warning("Aucun poème correspondant trouvé.")


# Intégration de la navigation
page = st.sidebar.radio("Navigation", ["Home", "Compilateur"])

if page == "Home":
    home_page()
elif page == "Compilateur":
    compilateur_page()



