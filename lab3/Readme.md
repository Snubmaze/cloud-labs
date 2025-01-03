### 3 лаба ###

Нам нужно будет написать два ci/cd.
Для написания этой лабороторной работы пришлось посоветоваться с dev-опсом с текущего проекта, чтобы узнать более реальные(из "практики") проблемы написания ci/cd файлов
# Что насчет плохого ci/cd? #

```
name: bad workflow

on: push

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v2

    - name: Install dependencies
      run: sudo apt-get install -y dotnet-sdk-8.0

    - name: Restore dependencies
      run: dotnet restore

    - name: Build
      run: dotnet build

    - name: Test
      run: dotnet test
    

  deploy:
    needs: build
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v2

    - name: Deploy to Production
      run: echo "Deploying to Production"
```
## Что же тут не так ? ##

1. Отсутствие управления версиями checkout: Используется общая версия v2, что может привести к несовместимости в будущем (без указания конкретной версии могут возникнуть несовместимости при обновлениях Actions. Новые версии могут изменить поведение).
2. Неправильная установка зависимостей: Установка SDK с помощью apt-get в CI/CD может быть медленной и ненадежной (установка пакетов через apt-get не всегда стабильна).
3. Нет указания точной ветки для деплоя: Отсутствует проверка на деплой только с ветки main(может привести к деплою неподготовленного кода).
4. Нет ограничения времени выполнения задач: Длительные задачи могут блокировать выполнение (задачи не имеют ограничения по времени. Если какая-то из них зависнет или будет выполняться слишком долго, workflow попросту может не завершится в разумные сроки).
5. Отсутствует кеширование зависимостей. Из за этого каждый раз будем заново устнавливать записимости.

# Что насчет хорошего  ci/cd? #


```
name: good workflow

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

jobs:
  build:
    runs-on: ubuntu-22.04
    timeout-minutes: 10

    steps:
    - name: Checkout code
      uses: actions/checkout@v2.4.0

    - name: Cache .NET packages
      uses: actions/cache@v3
      with:
        path: ~/.nuget/packages
        key: ${{ runner.os }}-nuget-${{ hashFiles('**/*.csproj') }}
        restore-keys: |
          ${{ runner.os }}-nuget-

    - name: Setup .NET SDK
      uses: actions/setup-dotnet@v1
      with:
        dotnet-version: '8.0.x'

    - name: Restore dependencies
      run: dotnet restore MyDotNetApp/MyDotNetApp.csproj

    - name: Build
      run: dotnet build MyDotNetApp/MyDotNetApp.csproj --no-restore

    - name: Test
      run: dotnet test MyDotNetApp/MyDotNetApp.csproj --no-build

    - name: Save build artifact
      uses: actions/upload-artifact@v3
      with:
        name: app-build
        path: MyDotNetApp/bin/Debug/net8.0/*.dll

    

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'

    steps:
    - name: Checkout code
      uses: actions/checkout@v2.4.0
    - name: Download build artifact
      uses: actions/download-artifact@v3
      with:
        name: app-build

    - name: Setup .NET SDK
      uses: actions/setup-dotnet@v1
      with:
        dotnet-version: '8.0.x'

    - name: Deploy to Production
      run: echo "Deploying to Production"

```

## Исправленные ошибки ##

1. Использование конкретной версии checkout: Теперь используется стабильная версия v2.4.0 для большей предсказуемости (в исправленном варианте указывается конкретная версия @v2.4.0, что фиксирует использование стабильной версии, которая не изменится без явного обновления).
2. Правильная установка зависимостей через actions: SDK устанавливается через GitHub Action, что быстрее и стабильнее (использование Action setup-dotnet для установки .NET SDK ускоряет процесс, обеспечивает стабильность и дает полный контроль над версией SDK).
3. Деплой только с ветки main: Добавлено условие для деплоя только при пуше в ветку main (добавление условия if: github.ref == 'refs/heads/main' гарантирует, что деплой произойдет только из ветки main.).
4. Ограничение времени выполнения: Ограничено время выполнения сборки до 10 минут (timeout-minutes: 10).
5. Добавлено кеширование зависимотей:
```
uses: actions/cache@v3
      with:
        path: ~/.nuget/packages
        key: ${{ runner.os }}-nuget-${{ hashFiles('**/*.csproj') }}
        restore-keys: |
          ${{ runner.os }}-nuget-
```

## Что-то типо конца ##
Перед импровизированным выводом нужно уточнить - добавлены строки в фактический good-workflow.yml : - name: Set execute permission for the script
      run: chmod +x ./run-scripts.sh

и чудо! Все получилось:
![alt text](image.png)


Хотелось бы подметить конечно же саму лабораторную работу - интересная идея, мы попытались совершить интересное "исполнение" этой лабы, сделав её более приближенной к текущим задачам связанным с дотнетом. Но еще хотелось бы подметить - неподдельный интерес к "dev-ops moment". Мы, как разработчики онли бэка(может немного фронт) - испытали по-настоящему интерес к может быть и рутине, но интересным вещам девопсам. Всегда прикольно и интересно писать код, но когда отдаешь свой проект девопсу - его работа в написании cicd, ты с одной стороны "освобождаешься" от его работы, тебе не нужно писать cicd файлы. НО когда именно ТЫ САМ своими ручками настраиваешь cicd, продумываешь всю логику данных файлов, ты чувствуешь "гордость" за банально самого себя, потому что ты не просто написал код, но и еще правильно настроил интеграцию и доставку своего творения, чувствуешь свою работу от начала до самого конца, понимаешь каждый шаг и каждое действие через которые проходит твой код. 
