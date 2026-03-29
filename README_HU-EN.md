# myRadio Music Server

<p align="center">
  <!-- 
  -->
  <img src="https://img.shields.io/github/downloads/gidano/myRadio-Music-Server/total?style=for-the-badge&cacheSeconds=60" alt="Total Downloads">
  <img src="https://img.shields.io/github/stars/gidano/myRadio-Music-Server?style=for-the-badge" alt="Stars">
  <img src="https://img.shields.io/github/repo-size/gidano/myRadio-Music-Server?style=for-the-badge" alt="Repo size">
</p>

Egy könnyen használható Windows alkalmazás, amely a számítógépedet **zenei streaming szerverré** alakítja **ESP32 alapú (myRadio, yoRadio, egyéb webrádiók) webrádiók** számára.

Az alkalmazás automatikusan **lejátszási listákat generál** a zenei mappádból, majd HTTP szerveren keresztül elérhetővé teszi őket, így a rádió közvetlenül a PC-ről tud zenét streamelni.

**Python telepítés nem szükséges**, az alkalmazás egyetlen EXE fájlként fut.

---

## Képernyőkép

![myRadio Music Server](https://github.com/gidano/myRadio-Music-Server/blob/main/myradio.music.server.jpg)

---

# Főbb funkciók

- Egyszerű **Windows grafikus felület**
- **Egyetlen EXE fájl** – Python nélkül fut
- **Magyar / Angol nyelv**
- Automatikus **playlist generálás**
- Albumonkénti lejátszási listák
- Automatikus **IP felismerés**
- Beépített **HTTP zenei szerver**
- Kompatibilis az **ESP32 myRadio firmware-rel**
- Windows **Dark / Light theme felismerés**
- Playlist URL-ek másolása egy kattintással
- Valós idejű szerver napló

---

# Generált lejátszási listák

A szerver indulásakor a program az alábbi fájlokat hozza létre a zenei mappában:


playlist.m3u
playlist_shuffle.m3u
album_playlists/*.m3u


Példa könyvtárszerkezet:


Music/
├── playlist.m3u
├── playlist_shuffle.m3u
├── album_playlists/
│ ├── Pink_Floyd.m3u
│ ├── Metallica.m3u
│ └── Daft_Punk.m3u


Ha a zenei könyvtár változik, a playlist-ek automatikusan frissülnek.

---

# Működés

Az alkalmazás egy kis HTTP szervert indít a számítógépen:


http://IP_CÍM:PORT/


Példa playlist URL:


http://192.168.31.101:8000/playlist.m3u


Ezt az URL-t kell megadni a **myRadio ESP32 webrádióban**, amely így közvetlenül a számítógépről játssza le a zenét.

---

# Használat

1. Indítsd el a **myRadio Music Server** alkalmazást
2. Válaszd ki a **zenei mappát**
3. Kattints az **Indítás** gombra
4. Másold ki a **playlist URL-t**
5. Add meg ezt a címet a **myRadio rádióban**

Ennyi.

A rádió ezután közvetlenül a számítógépedről fog zenét streamelni.

---

# Letöltés

A legfrissebb verzió innen tölthető le:

[myRadio Music Server](https://github.com/gidano/myRadio-Music-Server/releases/tag/1.1)

---

# Technikai részletek

HTTP szerver:


http.server.SimpleHTTPRequestHandler
ThreadingTCPServer


Playlist encoding:


UTF-8 BOM


A fájl URL-ek automatikusan kódolásra kerülnek, így a speciális karaktereket tartalmazó fájlnevek is működnek.

---

# Szerző

gidano

---

## EN ##

# myRadio Music Server

<p align="center">
  <!-- 
  -->
  <img src="https://img.shields.io/github/downloads/gidano/myRadio-Music-Server/total?style=for-the-badge&cacheSeconds=60" alt="Total Downloads">
  <img src="https://img.shields.io/github/stars/gidano/myRadio-Music-Server?style=for-the-badge" alt="Stars">
  <img src="https://img.shields.io/github/repo-size/gidano/myRadio-Music-Server?style=for-the-badge" alt="Repo size">
</p>

An easy-to-use Windows application that turns your computer into a **music streaming server** for **ESP32-based web radios (myRadio, yoRadio, and others)**.

The application automatically **generates playlists** from your music folder and makes them available via an HTTP server, allowing your radio to stream music directly from your PC.

**No Python installation required**, the application runs as a single EXE file.

---

## Screenshot

![myRadio Music Server](https://github.com/gidano/myRadio-Music-Server/blob/main/myradio.music.server.jpg)

---

# Main Features

- Simple **Windows graphical interface**
- **Single EXE file** – runs without Python
- **Hungarian / English language**
- Automatic **playlist generation**
- Per-album playlists
- Automatic **IP detection**
- Built-in **HTTP music server**
- Compatible with **ESP32 myRadio firmware**
- Windows **Dark / Light theme detection**
- One-click playlist URL copy
- Real-time server log

---

# Generated Playlists

When the server starts, the application creates the following files in the music folder:


playlist.m3u
playlist_shuffle.m3u
album_playlists/*.m3u


Example directory structure:


Music/
├── playlist.m3u
├── playlist_shuffle.m3u
├── album_playlists/
│ ├── Pink_Floyd.m3u
│ ├── Metallica.m3u
│ └── Daft_Punk.m3u


If the music library changes, the playlists are updated automatically.

---

# How It Works

The application starts a small HTTP server on your computer:


http://IP_ADDRESS:PORT/


Example playlist URL:


http://192.168.31.101:8000/playlist.m3u


This URL should be entered into the **myRadio ESP32 web radio**, which will then play music directly from your computer.

---

# Usage

1. Start the **myRadio Music Server** application
2. Select your **music folder**
3. Click the **Start** button
4. Copy the **playlist URL**
5. Enter this URL into your **myRadio radio**

That’s it.

The radio will then stream music directly from your computer.

---

# Download

The latest version can be downloaded here:

[myRadio Music Server](https://github.com/gidano/myRadio-Music-Server/releases/tag/1.1)

---

# Technical Details

HTTP server:


http.server.SimpleHTTPRequestHandler
ThreadingTCPServer


Playlist encoding:


UTF-8 BOM


File URLs are automatically encoded, so filenames with special characters are supported.

---

# Author

gidano
