from prompt_toolkit import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.widgets import Box, Frame
from prompt_toolkit.application.current import get_app
from prompt_toolkit.formatted_text import ANSI
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.margins import ScrollbarMargin
from rich.console import Console
from rich.text import Text
from prompt_toolkit.layout.dimension import D

console = Console()

class RichCheckboxList:
    def __init__(self, choices, preselected_indices=None):
        self.choices = choices
        self.selected = [False] * len(choices)
        if preselected_indices:
            for idx in preselected_indices:
                if 0 <= idx < len(self.selected):
                    self.selected[idx] = True
        self.current = 0
        self._scroll_offset = 0

        # Repère les indices des titres de groupe pour la sélection groupée
        self.group_indices = []
        for i, (label, _) in enumerate(choices):
            if "[bold underline]" in label:
                self.group_indices.append(i)

        # Calcul dynamique de la hauteur de la fenêtre
        max_visible = 15
        nb_choices = len(self.choices)
        visible_height = min(nb_choices, max_visible)
        self._visible_height = visible_height

        self.control = FormattedTextControl(self.get_formatted_text, key_bindings=self.get_key_bindings())
        self.window = Window(
            content=self.control,
            always_hide_cursor=True,
            right_margins=[ScrollbarMargin(display_arrows=True)],
            wrap_lines=False,
            height=D(preferred=visible_height, max=max_visible)
        )
        self.container = Box(
            Frame(self.window, title="Sélectionnez les modèles (Espace pour cocher, Entrée pour valider)"),
            padding=1
        )

    def get_formatted_text(self):
        lines = []
        import re
        visible_height = self._visible_height
        total = len(self.choices)
        # Calcul du scroll pour que l'élément courant soit toujours visible
        if self.current < self._scroll_offset:
            self._scroll_offset = self.current
        elif self.current >= self._scroll_offset + visible_height:
            self._scroll_offset = self.current - visible_height + 1

        start = self._scroll_offset
        end = min(start + visible_height, total)

        for i in range(start, end):
            label, style = self.choices[i]
            # Affichage de la case pour les groupes : [x] si tout coché, [ ] si tout décoché, [~] si partiel
            if i in self.group_indices:
                # Détermine la plage du groupe
                start_g = i + 1
                end_g = next((gi for gi in self.group_indices if gi > i), len(self.choices))
                checked = [self.selected[j] for j in range(start_g, end_g)]
                if checked and all(checked):
                    prefix = "[x]"
                elif checked and any(checked):
                    prefix = "[~]"
                else:
                    prefix = "[ ]"
            else:
                prefix = "[x]" if self.selected[i] else "[ ]"
            # On veut appliquer le style à chaque mot individuellement selon les tags
            fragments = []
            # Ajout du support pour [italic]...[/italic]
            pattern = re.compile(r"\[([a-zA-Z0-9_ ]+)\](.*?)\[/[a-zA-Z0-9_ ]+\]")
            last_end = 0
            for m in pattern.finditer(label):
                # Texte avant le tag
                if m.start() > last_end:
                    fragments.append((label[last_end:m.start()], None))
                # Texte dans le tag
                tag = m.group(1)
                frag_text = m.group(2)
                fragments.append((frag_text, tag))
                last_end = m.end()
            # Texte après le dernier tag
            if last_end < len(label):
                fragments.append((label[last_end:], None))
            # Construction du Text avec styles
            line = Text()
            line.append(f"{prefix} ")
            for frag_text, frag_style in fragments:
                if frag_style:
                    # On applique le style du tag uniquement (ex: "bold", "cyan", "italic", etc.)
                    line.append(frag_text, style=frag_style)
                else:
                    line.append(frag_text, style=style)
            if i == self.current:
                line.stylize("reverse")
            line.append("\n")
            lines.append(line)
        def text_to_ansi(text_obj):
            with console.capture() as capture:
                console.print(text_obj, end="")
            return capture.get()
        return ANSI("".join(text_to_ansi(line) for line in lines))

    def get_key_bindings(self):
        kb = KeyBindings()

        @kb.add('up')
        @kb.add('k')
        def _(event):
            self.current = (self.current - 1) % len(self.choices)
            event.app.invalidate()

        @kb.add('down')
        @kb.add('j')
        def _(event):
            self.current = (self.current + 1) % len(self.choices)
            event.app.invalidate()

        @kb.add(' ')
        def _(event):
            # Si on est sur un titre de groupe, toggle tout le groupe
            if self.current in self.group_indices:
                start = self.current + 1
                # Trouve la fin du groupe (prochain titre ou fin)
                end = next((i for i in self.group_indices if i > self.current), len(self.choices))
                # Détermine l'état à appliquer (si au moins un non coché -> tout cocher, sinon tout décocher)
                any_unchecked = any(not self.selected[i] for i in range(start, end))
                for i in range(start, end):
                    self.selected[i] = any_unchecked
            else:
                self.selected[self.current] = not self.selected[self.current]
            event.app.invalidate()

        @kb.add('enter')
        def _(event):
            event.app.exit(result=[i for i, checked in enumerate(self.selected) if checked])

        @kb.add('c-c')
        @kb.add('q')
        def _(event):
            event.app.exit(result=None)

        return kb

    def run(self):
        app = Application(layout=Layout(self.container), key_bindings=self.get_key_bindings(), full_screen=False)
        return app.run()

if __name__ == "__main__":
    # Exemple d'utilisation
    choices = [
        ("Flux (vae) ae.safetensors", "magenta"),
        ("[bold cyan]WAN21[/bold cyan] (loras) Su_MCraft_Ep60.safetensors", "cyan"),
        ("[bold]HiDream[/bold] (diffusion_models) hidream_i1_fast_fp8.safetensors", "green"),
    ]
    selector = RichCheckboxList(choices)
    result = selector.run()
    if result is not None:
        print("\nVous avez sélectionné :")
        for idx in result:
            print(f"- {choices[idx][0]}")
    else:
        print("\nSélection annulée.")
