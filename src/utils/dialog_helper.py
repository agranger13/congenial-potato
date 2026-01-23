"""
Helper pour la création de dialogs MDDialog.
Centralise la logique de création pour éviter la duplication de code.
"""
from typing import Callable, List, Optional, Any
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.list import MDList, OneLineListItem

from constants import DIALOG_LIST_HEIGHT, DIALOG_CONTENT_HEIGHT


class DialogHelper:
    """Helper statique pour créer différents types de dialogs."""

    @staticmethod
    def show_info(title: str, message: str) -> MDDialog:
        """
        Affiche un dialog d'information simple avec un bouton OK.

        Args:
            title: Titre du dialog
            message: Message à afficher

        Returns:
            L'instance MDDialog créée
        """
        dialog = MDDialog(
            title=title,
            text=message,
            buttons=[
                MDRectangleFlatButton(
                    text="OK",
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()
        return dialog

    @staticmethod
    def show_confirm(
        title: str,
        message: str,
        on_confirm: Callable[[], None],
        confirm_text: str = "CONFIRM",
        cancel_text: str = "CANCEL"
    ) -> MDDialog:
        """
        Affiche un dialog de confirmation avec boutons Cancel/Confirm.

        Args:
            title: Titre du dialog
            message: Message à afficher
            on_confirm: Callback appelé lors de la confirmation
            confirm_text: Texte du bouton de confirmation
            cancel_text: Texte du bouton d'annulation

        Returns:
            L'instance MDDialog créée
        """
        dialog = MDDialog(
            title=title,
            text=message,
            buttons=[
                MDRectangleFlatButton(
                    text=cancel_text,
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRectangleFlatButton(
                    text=confirm_text,
                    on_release=lambda x: (dialog.dismiss(), on_confirm())
                )
            ]
        )
        dialog.open()
        return dialog

    @staticmethod
    def show_custom(
        title: str,
        content: Any,
        buttons: Optional[List[tuple]] = None,
        on_dismiss: Optional[Callable[[], None]] = None
    ) -> MDDialog:
        """
        Affiche un dialog avec contenu personnalisé.

        Args:
            title: Titre du dialog
            content: Widget de contenu personnalisé
            buttons: Liste de tuples (text, callback) pour les boutons
            on_dismiss: Callback optionnel appelé à la fermeture

        Returns:
            L'instance MDDialog créée
        """
        dialog_buttons = []
        dialog = None

        def create_dialog():
            nonlocal dialog
            if buttons:
                for text, callback in buttons:
                    if callback is None:
                        btn = MDRectangleFlatButton(
                            text=text,
                            on_release=lambda x: dialog.dismiss()
                        )
                    else:
                        btn = MDRectangleFlatButton(
                            text=text,
                            on_release=lambda x, cb=callback: cb(dialog)
                        )
                    dialog_buttons.append(btn)

            dialog = MDDialog(
                title=title,
                type="custom",
                content_cls=content,
                buttons=dialog_buttons
            )

            if on_dismiss:
                dialog.bind(on_dismiss=lambda *args: on_dismiss())

            return dialog

        dialog = create_dialog()
        dialog.open()
        return dialog

    @staticmethod
    def show_list_selection(
        title: str,
        items: List[str],
        on_select: Callable[[str], None],
        cancel_text: str = "CANCEL"
    ) -> MDDialog:
        """
        Affiche un dialog avec une liste scrollable d'éléments sélectionnables.

        Args:
            title: Titre du dialog
            items: Liste des éléments à afficher
            on_select: Callback appelé avec l'élément sélectionné
            cancel_text: Texte du bouton d'annulation

        Returns:
            L'instance MDDialog créée
        """
        container = MDBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=DIALOG_LIST_HEIGHT
        )

        scroll = MDScrollView()
        list_view = MDList()

        dialog = None

        def on_item_click(item_text):
            def callback(instance):
                dialog.dismiss()
                on_select(item_text)
            return callback

        for item in items:
            list_item = OneLineListItem(text=item)
            list_item.bind(on_release=on_item_click(item))
            list_view.add_widget(list_item)

        scroll.add_widget(list_view)
        container.add_widget(scroll)

        dialog = MDDialog(
            title=title,
            type="custom",
            content_cls=container,
            buttons=[
                MDRectangleFlatButton(
                    text=cancel_text,
                    on_release=lambda x: dialog.dismiss()
                )
            ]
        )
        dialog.open()
        return dialog

    @staticmethod
    def show_input(
        title: str,
        fields: List[dict],
        on_save: Callable[[dict], None],
        save_text: str = "SAVE",
        cancel_text: str = "CANCEL"
    ) -> MDDialog:
        """
        Affiche un dialog avec des champs de saisie.

        Args:
            title: Titre du dialog
            fields: Liste de dictionnaires décrivant les champs
                    Chaque dict: {'name': str, 'hint': str, 'value': str, 'password': bool}
            on_save: Callback appelé avec un dict {name: value} pour chaque champ
            save_text: Texte du bouton de sauvegarde
            cancel_text: Texte du bouton d'annulation

        Returns:
            L'instance MDDialog créée
        """
        height = len(fields) * 60 + 30
        content = MDBoxLayout(
            orientation='vertical',
            spacing='10dp',
            size_hint_y=None,
            height=f"{height}dp"
        )

        text_fields = {}
        for field in fields:
            tf = MDTextField(
                hint_text=field.get('hint', ''),
                text=field.get('value', ''),
                mode="rectangle",
                password=field.get('password', False)
            )
            text_fields[field['name']] = tf
            content.add_widget(tf)

        def on_save_click(dialog):
            values = {name: tf.text.strip() for name, tf in text_fields.items()}
            on_save(values, dialog)

        dialog = MDDialog(
            title=title,
            type="custom",
            content_cls=content,
            buttons=[
                MDRectangleFlatButton(
                    text=cancel_text,
                    on_release=lambda x: dialog.dismiss()
                ),
                MDRectangleFlatButton(
                    text=save_text,
                    on_release=lambda x: on_save_click(dialog)
                )
            ]
        )
        dialog.open()
        return dialog
