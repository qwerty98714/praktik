import flet as ft
import requests
import sqlite3
from deep_translator import GoogleTranslator

translator_ru_en = GoogleTranslator(source="ru", target="en")
translator_en_ru = GoogleTranslator(source="en", target="ru")

def init_db():
    conn = sqlite3.connect("favorites.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            meal_id TEXT PRIMARY KEY,
            title TEXT,
            image_url TEXT
        )
    """)
    conn.commit()
    conn.close()

def add_to_favorites(meal_id, title, image_url):
    conn = sqlite3.connect("favorites.db")
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO favorites (meal_id, title, image_url) VALUES (?, ?, ?)",
                       (meal_id, title, image_url))
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    conn.close()

def remove_from_favorites(meal_id):
    conn = sqlite3.connect("favorites.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM favorites WHERE meal_id = ?", (meal_id,))
    conn.commit()
    conn.close()

def is_favorite(meal_id):
    conn = sqlite3.connect("favorites.db")
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM favorites WHERE meal_id = ?", (meal_id,))
    result = cursor.fetchone() is not None
    conn.close()
    return result

def get_last_favorite():
    conn = sqlite3.connect("favorites.db")
    cursor = conn.cursor()
    cursor.execute("SELECT meal_id, title, image_url FROM favorites ORDER BY rowid DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return row

def get_all_favorites():
    conn = sqlite3.connect("favorites.db")
    cursor = conn.cursor()
    cursor.execute("SELECT meal_id, title, image_url FROM favorites ORDER BY rowid DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

def main(page: ft.Page):
    init_db()
    page.title = "Culinary Mastermind"
    page.window.frameless = True
    page.window.width = 380
    page.window.height = 800
    page.window.resizable = False

    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.padding = 0
    page.bgcolor = "#2C2C3E"

    header_text = ft.Text(
        value="Culinary Mastermind",
        size=32,
        weight=ft.FontWeight.BOLD,
        color=ft.Colors.WHITE,
        font_family="Poppins",
    )

    subheader_text = ft.Text(
        value="Готовьте шедевры из того, что есть в холодильнике!",
        size=18,
        color=ft.Colors.GREY_300,
        font_family="Roboto",
    )

    def recipe_card(title: str, prep_time: int, calories: int, image_url: str):
        return ft.Card(
            width=160,
            height=250,
            content=ft.Container(
                bgcolor="#1F1F2A",
                padding=10,
                border_radius=ft.border_radius.all(15),
                content=ft.Column(
                    spacing=3,
                    controls=[
                        ft.Image(src=image_url, width=120, height=50, fit=ft.ImageFit.COVER),
                        ft.Text(
                            title,
                            color=ft.Colors.WHITE,
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            font_family="Poppins",
                        ),
                        ft.Text(
                            f"Время: {prep_time} мин",
                            color=ft.Colors.GREY_300,
                            size=14,
                            font_family="Roboto",
                        ),
                        ft.Text(
                            f"Калории: {calories}",
                            color=ft.Colors.GREY_300,
                            size=14,
                            font_family="Roboto",
                        ),
                        ft.ElevatedButton(
                            text="Подробнее",
                            bgcolor=ft.Colors.PINK_400,
                            color=ft.Colors.WHITE,
                            height=40,
                            style=ft.ButtonStyle(padding=5),
                            on_click=lambda e: print(f"Подробности рецепта: {title}"),
                        ),
                    ],
                ),
            ),
            elevation=10,
        )

    recipes_row = ft.Row(
        spacing=10,
        scroll=ft.ScrollMode.AUTO,
        controls=[
            recipe_card("Паста с томатами", prep_time=20, calories=350, image_url="https://via.placeholder.com/120x50"),
            recipe_card("Салат с авокадо", prep_time=15, calories=250, image_url="https://via.placeholder.com/120x50"),
            recipe_card("Суп из тыквы", prep_time=30, calories=400, image_url="https://via.placeholder.com/120x50"),
        ],
    )

    def load_last_favorite():
        row = get_last_favorite()
        if row is None:
            return ft.Text("Нет избранного", color=ft.Colors.WHITE, size=16)
        meal_id, title, image_url = row
        return ft.Container(
            padding=10,
            bgcolor="#2E2F45",
            border_radius=ft.border_radius.all(10),
            margin=ft.margin.symmetric(vertical=5),
            content=ft.Row(
                spacing=10,
                controls=[
                    ft.Icon(ft.Icons.FAVORITE, color=ft.Colors.PINK_400, size=24),
                    ft.Text(title, color=ft.Colors.WHITE, size=16, font_family="Roboto", expand=True),
                    ft.ElevatedButton(
                        text="Подробнее",
                        bgcolor=ft.Colors.PINK_400,
                        color=ft.Colors.WHITE,
                        on_click=lambda e, m_id=meal_id: view_recipe(page, m_id)
                    )
                ],
            ),
        )

    last_fav_control = load_last_favorite()

    top_bar = ft.Row(
        [
            ft.IconButton(
                ft.Icons.MENU,
                icon_color=ft.Colors.WHITE,
                on_click=lambda e: open_side_menu(page),
            ),
            ft.Container(expand=1),
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
    )

    search_button_container = ft.Container(
        content=ft.IconButton(
            ft.Icons.SEARCH,
            icon_size=40,
            icon_color=ft.Colors.WHITE,
            bgcolor=ft.Colors.PINK_400,
            on_click=lambda e: open_search_screen(page),
        ),
        alignment=ft.Alignment(0, 1),
        margin=ft.margin.only(top=20),
    )

    main_content = ft.Column(
        width=page.window.width,
        spacing=20,
        alignment=ft.MainAxisAlignment.START,
        controls=[
            top_bar,
            header_text,
            subheader_text,
            recipes_row,
            ft.Text("Избранное", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE, font_family="Poppins"),
            last_fav_control,
        ],
    )

    side_menu = ft.Container(
        visible=False,
        expand=True,
        on_click=lambda e: close_side_menu(page),
        bgcolor=ft.Colors.with_opacity(0.5, ft.Colors.BLACK),
        content=ft.Row(
            expand=True,
            alignment=ft.MainAxisAlignment.START,
            controls=[
                ft.Container(
                    width=220,
                    bgcolor="#2E2F45",
                    padding=20,
                    content=ft.Column(
                        spacing=10,
                        controls=[
                            ft.Text("Меню", color=ft.Colors.WHITE, size=20, weight=ft.FontWeight.BOLD),
                            ft.Divider(color=ft.Colors.GREY_700),
                            ft.Container(
                                on_click=lambda e: favorites_menu_click(page),
                                content=ft.Row(
                                    spacing=5,
                                    controls=[
                                        ft.Icon(ft.Icons.FAVORITE, color=ft.Colors.PINK_400),
                                        ft.Text("Избранное", color=ft.Colors.WHITE, size=16),
                                    ],
                                ),
                            ),
                        ],
                    ),
                ),
                ft.Container(expand=True),
            ],
        ),
    )

    def close_side_menu(page: ft.Page):
        side_menu.visible = False
        page.update()

    def open_side_menu(page: ft.Page):
        side_menu.visible = True
        page.update()

    def favorites_menu_click(page: ft.Page):
        close_side_menu(page)
        open_favorites_screen(page)

    page.controls.clear()
    page.add(
        ft.Stack(
            expand=True,
            controls=[
                main_content,
                side_menu,
            ],
        ),
        search_button_container,
    )
    page.update()

def open_search_screen(page: ft.Page):
    page.controls.clear()
    top_bar = ft.Row(
        [
            ft.IconButton(ft.Icons.ARROW_BACK, icon_color=ft.Colors.WHITE, icon_size=28, on_click=lambda e: main(page)),
        ],
        alignment=ft.MainAxisAlignment.START,
    )
    search_field = ft.TextField(
        label="Введите ингредиенты (на русском)",
        autofocus=True,
        bgcolor="#2C2E3E",
        border_radius=ft.border_radius.all(20),
        color=ft.Colors.WHITE,
        prefix_icon=ft.Icon(ft.Icons.SEARCH, color=ft.Colors.PINK_400, size=24),
        height=55,
        width=page.window.width - 40,
        text_size=18,
    )
    results_column_ref = ft.Ref[ft.Column]()
    results_column = ft.Column(
        ref=results_column_ref,
        scroll=ft.ScrollMode.AUTO,
        expand=True,
        spacing=10,
    )
    def search_handler(e):
        perform_search(page, search_field.value, results_column_ref)
    search_field.on_submit = search_handler

    page.add(
        ft.Column(
            width=page.window.width,
            spacing=20,
            expand=True,
            controls=[
                top_bar,
                ft.Container(padding=ft.padding.all(20), content=search_field),
                results_column,
            ],
        )
    )
    page.update()

def perform_search(page: ft.Page, query: str, results_ref: ft.Ref[ft.Column]):
    results_column = results_ref.current
    results_column.controls.clear()
    loading_container = ft.Container(
        content=ft.ProgressRing(width=60, height=60, stroke_width=8, color=ft.Colors.PINK_400),
        alignment=ft.alignment.center,
        padding=20,
    )
    results_column.controls.append(loading_container)
    page.update()

    translated_query = translator_ru_en.translate(query)
    url = f"https://www.themealdb.com/api/json/v1/1/filter.php?i={translated_query}"
    try:
        resp = requests.get(url)
        data = resp.json()
        meals = data.get("meals")
    except Exception as e:
        print("Ошибка при запросе:", e)
        meals = None

    results_column.controls.clear()
    if meals:
        for meal in meals:
            meal_id = meal.get("idMeal")
            title_en = meal.get("strMeal", "")
            image_url = meal.get("strMealThumb", "")
            title_ru = translator_en_ru.translate(title_en)
            card = ft.Container(
                bgcolor="#1F1F2A",
                border_radius=ft.border_radius.all(15),
                padding=15,
                margin=ft.margin.symmetric(horizontal=10),
                content=ft.Column(
                    spacing=12,
                    controls=[
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.Container(
                                    border_radius=ft.border_radius.all(15),
                                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                                    content=ft.Image(
                                        src=image_url,
                                        width=page.window.width - 60,
                                        height=180,
                                        fit=ft.ImageFit.COVER,
                                    ),
                                ),
                            ],
                        ),
                        ft.Text(
                            title_ru,
                            color=ft.Colors.WHITE,
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            font_family="Montserrat",
                        ),
                        ft.ElevatedButton(
                            text="Подробнее",
                            bgcolor=ft.Colors.PINK_400,
                            color=ft.Colors.WHITE,
                            height=48,
                            style=ft.ButtonStyle(padding=8),
                            on_click=lambda e, m_id=meal_id: view_recipe(page, m_id),
                        ),
                    ],
                ),
            )
            results_column.controls.append(card)
    else:
        results_column.controls.append(ft.Text("Рецепты не найдены", color=ft.Colors.WHITE, size=20))
    page.update()

def view_recipe(page: ft.Page, meal_id: str):
    url = f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={meal_id}"
    try:
        resp = requests.get(url)
        data = resp.json()
        meal = data.get("meals")[0]
    except Exception as e:
        print("Ошибка при получении деталей рецепта:", e)
        meal = None

    if meal:
        title_en = meal.get("strMeal", "")
        instructions_en = meal.get("strInstructions", "")
        image_url = meal.get("strMealThumb", "")
        category_en = meal.get("strCategory") or ""
        area_en = meal.get("strArea") or ""
        tags_en = meal.get("strTags") or ""

        title_ru = translator_en_ru.translate(title_en)
        instructions_ru = translator_en_ru.translate(instructions_en)
        category_ru = translator_en_ru.translate(category_en) if category_en else "—"
        area_ru = translator_en_ru.translate(area_en) if area_en else "—"
        tags_ru = translator_en_ru.translate(tags_en) if tags_en else "—"

        instructions_lines = [line.strip() for line in instructions_ru.split('\n') if line.strip()]

        ingredients = []
        for i in range(1, 21):
            ing = meal.get(f"strIngredient{i}")
            measure = meal.get(f"strMeasure{i}")
            if ing and ing.strip():
                ing_text = f"{ing} - {measure}"
                ing_text_ru = translator_en_ru.translate(ing_text)
                ingredients.append(ing_text_ru)

        heart_button = ft.IconButton(
            icon=ft.Icons.FAVORITE if is_favorite(meal_id) else ft.Icons.FAVORITE_BORDER,
            icon_color=ft.Colors.PINK_400,
            icon_size=28,
        )
        def toggle_favorite(e):
            if is_favorite(meal_id):
                remove_from_favorites(meal_id)
                heart_button.icon = ft.Icons.FAVORITE_BORDER
            else:
                add_to_favorites(meal_id, title_ru, image_url)
                heart_button.icon = ft.Icons.FAVORITE
            heart_button.update()
        heart_button.on_click = toggle_favorite

        top_bar = ft.Row(
            [
                ft.IconButton(
                    ft.Icons.ARROW_BACK,
                    icon_color=ft.Colors.WHITE,
                    icon_size=28,
                    on_click=lambda e: open_search_screen(page)
                ),
                heart_button,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        def bullet_row(line_text: str):
            return ft.Row(
                spacing=8,
                controls=[
                    ft.Icon(ft.Icons.FIBER_MANUAL_RECORD, color=ft.Colors.PINK_400, size=26),
                    ft.Text(
                        line_text,
                        color=ft.Colors.WHITE,
                        size=18,
                        width=page.window.width - 80,
                        no_wrap=False,
                    ),
                ],
            )

        area_card = ft.Container(
            bgcolor="#34354A",
            border_radius=ft.border_radius.all(15),
            padding=ft.padding.symmetric(horizontal=10, vertical=8),
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=3,
                controls=[
                    ft.Icon(ft.Icons.PLACE, color=ft.Colors.PINK_400, size=24),
                    ft.Text(area_ru, color=ft.Colors.WHITE, size=18),
                ],
            ),
        )
        category_card = ft.Container(
            bgcolor="#34354A",
            border_radius=ft.border_radius.all(15),
            padding=ft.padding.symmetric(horizontal=10, vertical=8),
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=3,
                controls=[
                    ft.Icon(ft.Icons.CATEGORY, color=ft.Colors.PINK_400, size=24),
                    ft.Text(category_ru, color=ft.Colors.WHITE, size=18),
                ],
            ),
        )
        tags_card = ft.Container(
            bgcolor="#34354A",
            border_radius=ft.border_radius.all(15),
            padding=ft.padding.symmetric(horizontal=10, vertical=8),
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=3,
                controls=[
                    ft.Icon(ft.Icons.LABEL, color=ft.Colors.PINK_400, size=24),
                    ft.Text(tags_ru, color=ft.Colors.WHITE, size=18),
                ],
            ),
        )
        row_icons = ft.Row(
            spacing=20,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[area_card, category_card, tags_card],
        )

        image_container = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    border_radius=ft.border_radius.all(20),
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    content=ft.Image(
                        src=image_url,
                        width=page.window.width - 40,
                        height=220,
                        fit=ft.ImageFit.COVER,
                    ),
                ),
            ],
        )

        detail_column = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=20,
            controls=[
                image_container,
                ft.Text(
                    title_ru,
                    color=ft.Colors.WHITE,
                    size=28,
                    weight=ft.FontWeight.BOLD,
                    font_family="Montserrat",
                ),
                row_icons,
                ft.Text("Ингредиенты:", color=ft.Colors.PINK_400, size=22, weight=ft.FontWeight.BOLD),
                ft.Column(
                    spacing=8,
                    controls=[bullet_row(ing) for ing in ingredients],
                ),
                ft.Text("Инструкции:", color=ft.Colors.PINK_400, size=22, weight=ft.FontWeight.BOLD),
                ft.Column(
                    spacing=8,
                    controls=[bullet_row(line) for line in instructions_lines],
                ),
            ],
        )

        page.controls.clear()
        page.add(
            ft.Column(
                spacing=20,
                expand=True,
                controls=[
                    top_bar,
                    detail_column,
                ],
            )
        )
        page.update()
    else:
        print("Рецепт не найден или произошла ошибка.")

def open_favorites_screen(page: ft.Page):
    page.controls.clear()
    top_bar = ft.Row(
        [
            ft.IconButton(
                ft.Icons.ARROW_BACK,
                icon_color=ft.Colors.WHITE,
                icon_size=28,
                on_click=lambda e: main(page)
            ),
            ft.Container(expand=True),
        ],
        alignment=ft.MainAxisAlignment.START,
    )

    conn = sqlite3.connect("favorites.db")
    cursor = conn.cursor()
    cursor.execute("SELECT meal_id, title, image_url FROM favorites ORDER BY rowid DESC")
    favs = cursor.fetchall()
    conn.close()

    fav_controls = []
    if favs:
        for meal_id, title, image_url in favs:
            fav_controls.append(
                ft.Container(
                    padding=10,
                    bgcolor="#2E2F45",
                    border_radius=ft.border_radius.all(10),
                    margin=ft.margin.symmetric(vertical=5),
                    content=ft.Row(
                        spacing=10,
                        controls=[
                            ft.Icon(ft.Icons.FAVORITE, color=ft.Colors.PINK_400, size=24),
                            ft.Text(title, color=ft.Colors.WHITE, size=16, font_family="Roboto", expand=True),
                            ft.ElevatedButton(
                                text="Подробнее",
                                bgcolor=ft.Colors.PINK_400,
                                color=ft.Colors.WHITE,
                                on_click=lambda e, m_id=meal_id: view_recipe(page, m_id),
                            ),
                        ],
                    ),
                )
            )
    else:
        fav_controls.append(ft.Text("Избранное пустое", color=ft.Colors.WHITE, size=20))
    fav_column = ft.Column(
        controls=fav_controls,
        spacing=10,
    )

    page.add(
        ft.Column(
            spacing=20,
            expand=True,
            controls=[
                top_bar,
                ft.Text("Все избранные рецепты", color=ft.Colors.WHITE, size=24, weight=ft.FontWeight.BOLD, font_family="Montserrat"),
                ft.Container(expand=True, padding=ft.padding.all(20), content=fav_column),
            ],
        )
    )
    page.update()

def go_back(page: ft.Page):
    page.controls.clear()
    main(page)

if __name__ == "__main__":
    ft.app(target=main)
