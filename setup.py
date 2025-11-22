from setuptools import setup, find_packages

setup(
    name="digital_ruble_simulation",
    version="0.1.0",
    description="Имитационная модель цифрового рубля",
    author="Your Name", # Замените на своё имя
    author_email="your.email@example.com", # Замените на свой email
    # Указываем, что пакеты находятся в корне проекта (digital_ruble_simulation)
    # find_packages ищет папки с __init__.py
    # package_dir указывает, что корень пакетов начинается с '.', т.е. самой директории setup.py
    # packages - это список пакетов, которые нужно включить.
    # В нашем случае, основной пакет - это 'src', 'ui' и т.д., которые находятся внутри 'digital_ruble_simulation'.
    # find_packages() автоматически найдёт 'src' и 'ui', если они помечены как пакеты (__init__.py).
    # package_dir={'': '.'}, # Корень пакетов - текущая директория (не обязательно, если пакеты в корне)
    packages=find_packages(include=['digital_ruble_simulation', 'digital_ruble_simulation.*']), # Ищем пакеты, начинающиеся с digital_ruble_simulation
    # Альтернатива: явно перечислить пакеты
    # packages=[
    #     'digital_ruble_simulation',
    #     'digital_ruble_simulation.src',
    #     'digital_ruble_simulation.src.core',
    #     'digital_ruble_simulation.src.core.participants',
    #     'digital_ruble_simulation.src.data',
    #     'digital_ruble_simulation.src.data.models',
    #     'digital_ruble_simulation.src.ui',
    #     'digital_ruble_simulation.src.ui.tabs',
    # ],
    install_requires=[
        "sqlalchemy>=1.4",
        "matplotlib>=3.5",
    ],
    python_requires='>=3.6',
)