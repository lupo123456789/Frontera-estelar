import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler

def init_db():
    conn = sqlite3.connect('estelar.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS personajes (
        user_id INTEGER PRIMARY KEY,
        nombre TEXT,
        oficio TEXT,
        nivel INTEGER DEFAULT 1,
        experiencia INTEGER DEFAULT 0,
        oro INTEGER DEFAULT 500,
        nave_activa INTEGER DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS naves (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        dueno_id INTEGER,
        nombre TEXT,
        tipo TEXT DEFAULT "exploradora",
        nivel INTEGER DEFAULT 1,
        escudo INTEGER DEFAULT 100,
        blindaje INTEGER DEFAULT 50,
        armas INTEGER DEFAULT 1,
        bodega INTEGER DEFAULT 10,
        costo INTEGER DEFAULT 300
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS estadisticas (
        user_id INTEGER PRIMARY KEY,
        exp_completadas INTEGER DEFAULT 0,
        exp_falladas INTEGER DEFAULT 0,
        racha_actual INTEGER DEFAULT 0,
        mejor_racha INTEGER DEFAULT 0,
        total_oro_ganado INTEGER DEFAULT 0,
        total_est_ganado REAL DEFAULT 0,
        naves_perdidas INTEGER DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS naves_dano (
        nave_id INTEGER PRIMARY KEY,
        dano INTEGER DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS tripulacion (
        nave_id INTEGER,
        user_id INTEGER,
        oficio TEXT,
        listo INTEGER DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS tablon (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        capitan_id INTEGER,
        nombre_capitan TEXT,
        nave_nombre TEXT,
        nave_tipo TEXT,
        oficio_buscado TEXT,
        cantidad_total INTEGER DEFAULT 1,
        cantidad_actual INTEGER DEFAULT 0,
        activo INTEGER DEFAULT 1
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS tokens (
        user_id INTEGER PRIMARY KEY,
        balance REAL DEFAULT 0,
        total_ganado REAL DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS tokens (
        user_id INTEGER PRIMARY KEY,
        balance REAL DEFAULT 0,
        total_ganado REAL DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS stats_personaje (
        user_id INTEGER PRIMARY KEY,
        precision INTEGER DEFAULT 5,
        defensa INTEGER DEFAULT 5,
        extraccion INTEGER DEFAULT 5,
        velocidad INTEGER DEFAULT 5,
        suerte INTEGER DEFAULT 5,
        puntos_libres INTEGER DEFAULT 0
    )''')
    conn.commit()
    conn.close()

init_db()

TIPOS_NAVE = {
    "exploradora": {"nombre": "Exploradora", "escudo": 80, "blindaje": 40, "armas": 1, "bodega": 15, "costo": 300},
    "minera":     {"nombre": "Minera", "escudo": 100, "blindaje": 60, "armas": 0, "bodega": 40, "costo": 400},
    "combate":    {"nombre": "Combate", "escudo": 120, "blindaje": 100, "armas": 3, "bodega": 5, "costo": 600},
    "hibrida":    {"nombre": "Hibrida", "escudo": 100, "blindaje": 70, "armas": 2, "bodega": 20, "costo": 800}
}
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    
    conn = sqlite3.connect('estelar.db')
    c = conn.cursor()
    
    # Ver si ya vio el lore
    c.execute("SELECT vio_lore FROM jugadores_nuevos WHERE user_id=?", (user_id,))
    vio = c.fetchone()
    
    if not vio:
        # Es la primera vez - mostrar lore
        c.execute("INSERT INTO jugadores_nuevos (user_id, vio_lore) VALUES (?, 1)", (user_id,))
        conn.commit()
        conn.close()
        
        # Capítulo 1: Introducción
        await update.message.reply_text(
            "📖 *FRONTERA ESTELAR*\n\n"
            "*Año 2847. La humanidad se expandió por la galaxia durante siglos, colonizando miles de sistemas estelares.* "
            "Pero la ambición desmedida y las guerras corporativas fragmentaron la civilización. "
            "Las grandes flotas colapsaron, las rutas comerciales se desvanecieron y la comunicación interestelar se volvió un lujo.\n\n"
            "En medio del caos, surgió un mineral legendario: el *ESTELIO*. Un cristal azul brillante que emana una energía pura y casi infinita. "
            "Dicen que se formó en el corazón de estrellas moribundas, y que quien lo controle, controlará el destino de la galaxia.",
            parse_mode='Markdown'
        )
        
        # Capítulo 2: Los Sectores
        await update.message.reply_text(
            "🌍 *LOS TRES SECTORES*\n\n"
            "🟢 *HIGH SEC:* El último refugio de la civilización. Protegido por la Alianza de Sistemas Unidos. "
            "Seguro, pero el Estelio escasea.\n\n"
            "🟡 *LOW SEC:* La tierra de nadie. Piratas, estaciones abandonadas y tesoros ocultos. "
            "El doble de Estelio, pero sin protección.\n\n"
            "🔴 *NULL SEC:* El abismo estelar. Nadie controla este sector. "
            "El Estelio brilla 4 veces más, pero la muerte acecha en cada esquina. "
            "Solo los más valientes sobreviven.",
            parse_mode='Markdown'
        )
        
        # Capítulo 3: Los Oficios
        await update.message.reply_text(
            "🎭 *LOS OFICIOS*\n\n"
            "🛩️ *PILOTO:* Navega la nave, elige la ruta, esquiva el peligro. Sin piloto, no hay expedición.\n\n"
            "🔫 *ARMERO:* Controla las armas, defiende la nave, elimina amenazas. Sin armero, estás indefenso.\n\n"
            "⛏️ *MINERO:* Extrae el Estelio, optimiza la carga, encuentra tesoros. Sin minero, no hay riqueza.\n\n"
            "*Juntos, forman la tripulación perfecta. Por separado, son presa fácil.*",
            parse_mode='Markdown'
        )
        
        # Capítulo 4: El Estelio (Token EST)
        await update.message.reply_text(
            "💎 *EL ESTELIO*\n\n"
            "El Estelio no es solo un mineral. Es la sangre de estrellas muertas, cristalizada durante milenios en el vacío. "
            "Emite un brillo azul hipnótico y contiene una energía que desafía las leyes de la física.\n\n"
            "En el juego, el Estelio se representa como *tokens EST*. Los ganas en expediciones y "
            "cada 30 días puedes canjearlos por *USDT* reales en la red TON.\n\n"
            "Cuanto más peligroso el sector, más Estelio produces.",
            parse_mode='Markdown'
        )
        
        # Capítulo 5: Inicio
        await update.message.reply_text(
            "🚀 *TU HISTORIA COMIENZA*\n\n"
            "Llegas a la estación *Esperanza Estelar* en High Sec. Eres un desconocido con una nave prestada "
            "y un puñado de créditos. Pero tienes algo que el dinero no puede comprar: ambición.\n\n"
            "¿Serás un minero paciente, acumulando Estelio en High Sec?\n"
            "¿Un mercenario temerario, cazando piratas en Low Sec?\n"
            "¿O un legendario capitán de Null Sec, forjando tu leyenda en el abismo?\n\n"
            "*La Frontera Estelar no perdona. Pero tampoco olvida a sus héroes.*",
            parse_mode='Markdown'
        )
        
        # Mostrar menú de creación
        teclado = InlineKeyboardMarkup([
            [InlineKeyboardButton("🚀 Crear personaje", callback_data="crear_menu")],
            [InlineKeyboardButton("📖 Ver oficios", callback_data="oficios_info")]
        ])
        await update.message.reply_text(
            "⚔️ *FORJA TU TRIPULACIÓN. DOMINA LOS SECTORES. RECLAMA EL ESTELIO.* ⚔️\n\n"
            "Elige tu oficio y comienza tu aventura:",
            parse_mode='Markdown',
            reply_markup=teclado
        )
        return
    
    conn.close()
    
    # Si ya vio el lore, mostrar menú normal
    conn = sqlite3.connect('estelar.db')
    c = conn.cursor()
    c.execute("SELECT * FROM personajes WHERE user_id=?", (user_id,))
    p = c.fetchone()
    conn.close()
    
    if p:
        teclado = InlineKeyboardMarkup([
            [InlineKeyboardButton("Stats", callback_data="menu_stats")],
            [InlineKeyboardButton("Naves", callback_data="menu_nave")],
            [InlineKeyboardButton("Expediciones", callback_data="menu_exp")],
            [InlineKeyboardButton("Tablon", callback_data="menu_tablon")],
            [InlineKeyboardButton("Tripulacion", callback_data="menu_trip")],
            [InlineKeyboardButton("Publicar anuncio", callback_data="menu_publicar")],
            [InlineKeyboardButton("Cancelar anuncio", callback_data="menu_cancelar")],
            [InlineKeyboardButton("Tokens EST", callback_data="menu_tokens")],
            [InlineKeyboardButton("Ayuda", callback_data="menu_ayuda")],
            [InlineKeyboardButton("Reparar nave", callback_data="menu_reparar")],
        ])
        await update.message.reply_text(
            f"FRONTERA ESTELAR\n\nCapitan: {p[1]} ({p[2].capitalize()})\n\nElige una opcion:",
            reply_markup=teclado
        )
    else:
        teclado = InlineKeyboardMarkup([
            [InlineKeyboardButton("Crear personaje", callback_data="crear_menu")],
            [InlineKeyboardButton("Ver oficios", callback_data="oficios_info")]
        ])
        await update.message.reply_text(
            "Bienvenido de vuelta a la Frontera Estelar\n\nElige tu oficio y forma tu tripulacion.",
            reply_markup=teclado
        )

async def oficios_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    teclado = InlineKeyboardMarkup([[InlineKeyboardButton("Volver al menu", callback_data="volver_start")]])
    await query.edit_message_text(
        "Oficios disponibles:\n\n"
        "Piloto - Navega la nave.\n"
        "Armero - Controla las armas.\n"
        "Minero - Extrae recursos.",
        reply_markup=teclado
    )

async def crear_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    conn = sqlite3.connect('estelar.db')
    c = conn.cursor()
    c.execute("SELECT * FROM personajes WHERE user_id=?", (user_id,))
    if c.fetchone():
        conn.close()
        await query.edit_message_text("Ya tienes un personaje.")
        return
    conn.close()
    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("Piloto", callback_data="crear_piloto")],
        [InlineKeyboardButton("Armero", callback_data="crear_armero")],
        [InlineKeyboardButton("Minero", callback_data="crear_minero")]
    ])
    await query.edit_message_text("Elige tu oficio:", reply_markup=teclado)

async def crear_personaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    nombre = query.from_user.first_name
    oficios = {"crear_piloto": "piloto", "crear_armero": "armero", "crear_minero": "minero"}
    oficio = oficios.get(query.data)
    if not oficio:
        return
    conn = sqlite3.connect('estelar.db')
    c = conn.cursor()
    c.execute("INSERT INTO personajes (user_id, nombre, oficio) VALUES (?, ?, ?)", (user_id, nombre, oficio))
    conn.commit()
    conn.close()
    
    try:
        with open(f"img/personajes/{oficio}.jpg", "rb") as foto:
            await context.bot.send_photo(chat_id=user_id, photo=foto, caption=f"{nombre} - {oficio.capitalize()}\n\nPersonaje creado!\nOro inicial: 500")
    except:
        await context.bot.send_message(chat_id=user_id, text=f"{nombre} - {oficio.capitalize()} creado.\nOro: 500")
    
    teclado = InlineKeyboardMarkup([[InlineKeyboardButton("Volver al menu", callback_data="volver_start")]])
    await query.edit_message_text("Preparate para la aventura!", reply_markup=teclado)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        mensaje = query.edit_message_text
    else:
        user_id = update.message.from_user.id
        mensaje = update.message.reply_text
    
    conn = sqlite3.connect('estelar.db')
    c = conn.cursor()
    c.execute("SELECT * FROM personajes WHERE user_id=?", (user_id,))
    p = c.fetchone()
    if not p:
        conn.close()
        await mensaje("No tienes personaje.")
        return
    
    c.execute("SELECT * FROM stats_personaje WHERE user_id=?", (user_id,))
    s = c.fetchone()
    
    # Si no tiene stats, crearlos
    if not s:
        base = STATS_BASE.get(p[2], STATS_BASE["piloto"])
        c.execute("INSERT INTO stats_personaje (user_id, precision, defensa, extraccion, velocidad, suerte) VALUES (?, ?, ?, ?, ?, ?)",
                  (user_id, base["precision"], base["defensa"], base["extraccion"], base["velocidad"], base["suerte"]))
        conn.commit()
        c.execute("SELECT * FROM stats_personaje WHERE user_id=?", (user_id,))
        s = c.fetchone()
    
    c.execute("SELECT * FROM naves WHERE dueno_id=?", (user_id,))
    naves = c.fetchall()
    
    # Nave activa
    nave_activa = None
    for n in naves:
        if n[0] == p[6]:
            nave_activa = n
            break
    
    # Tripulación
    c.execute("SELECT tripulacion.oficio, personajes.nombre FROM tripulacion JOIN personajes ON tripulacion.user_id = personajes.user_id WHERE nave_id=?", (p[6],))
    trip = c.fetchall()
    
    conn.close()
    
    emoji_oficio = {"piloto": "🛩️", "armero": "🔫", "minero": "⛏️"}
    
    texto = f"📊 PERFIL DE {p[1].upper()}\n\n"
    texto += f"{emoji_oficio.get(p[2], '')} Oficio: {p[2].capitalize()}\n"
    texto += f"⭐ Nivel: {p[3]} | ✨ EXP: {p[4]}/{p[3]*100}\n"
    texto += f"💰 Oro: {p[5]} | 🛸 Naves: {len(naves)}\n\n"
    
    # Stats del personaje
    texto += "🎯 STATS DEL PERSONAJE:\n"
    texto += f"  🎯 Precisión: {s[1]}  |  🛡️ Defensa: {s[2]}\n"
    texto += f"  ⛏️ Extracción: {s[3]}  |  🚀 Velocidad: {s[4]}\n"
    texto += f"  🍀 Suerte: {s[5]}\n"
    if s[6] > 0:
        texto += f"  ⭐ Puntos libres: {s[6]} (usa botón Mejorar Stats)\n"
    texto += "\n"
    
    # Nave activa
    if nave_activa:
        texto += f"🛸 NAVE ACTIVA:\n"
        texto += f"  {nave_activa[2]} ({nave_activa[3]}) Nv.{nave_activa[4]}\n"
        texto += f"  🛡️ Escudo: {nave_activa[5]}  |  🔩 Blindaje: {nave_activa[6]}\n"
        texto += f"  🔫 Armas: {nave_activa[7]}  |  📦 Bodega: {nave_activa[8]}\n\n"
    else:
        texto += "🛸 NAVE ACTIVA: Ninguna\n\n"
    
    # Tripulación
    texto += "👥 TRIPULACIÓN:\n"
    texto += f"  {emoji_oficio.get(p[2], '')} {p[1]} ({p[2]}) - Capitán\n"
    if trip:
        for t in trip:
            texto += f"  {emoji_oficio.get(t[0], '')} {t[1]} ({t[0]})\n"
    else:
        texto += "  Sin tripulantes adicionales\n"
    
    # Si hay tripulación, mostrar stats combinados
    if nave_activa and trip:
        stats_trip = obtener_stats_tripulacion(p[6], user_id)
        bonus = stats_trip["bonus"]
        texto += f"\n📊 STATS COMBINADOS DE LA NAVE:\n"
        texto += f"  🎯 Precisión: {stats_trip['stats']['precision']} (+{bonus['exito']}% éxito)\n"
        texto += f"  🛡️ Defensa: {stats_trip['stats']['defensa']} (-{bonus['defensa']*2}% daño)\n"
        texto += f"  ⛏️ Extracción: {stats_trip['stats']['extraccion']} (+{bonus['extraccion']*2}% recursos)\n"
        texto += f"  🚀 Velocidad: {stats_trip['stats']['velocidad']} (-{bonus['velocidad']*2}s)\n"
        texto += f"  🍀 Suerte: {stats_trip['stats']['suerte']} (+{bonus['suerte']}% eventos)\n"
    
    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("Mejorar stats", callback_data="menu_stats_p")],
        [InlineKeyboardButton("Volver al menu", callback_data="volver_start")]
    ])
    
    try:
            await mensaje(texto, reply_markup=teclado)
    except:
        pass
async def ver_naves(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    conn = sqlite3.connect('estelar.db')
    c = conn.cursor()
    c.execute("SELECT nave_activa FROM personajes WHERE user_id=?", (user_id,))
    activa_id = c.fetchone()[0]
    c.execute("SELECT * FROM naves WHERE dueno_id=?", (user_id,))
    naves = c.fetchall()
    conn.close()
    if not naves:
        await query.edit_message_text("No tienes naves.")
        return
    
    for n in naves:
        if n[0] == activa_id:
            try:
                with open(f"img/naves/{n[3]}.jpg", "rb") as foto:
                    await context.bot.send_photo(chat_id=user_id, photo=foto, caption=f"NAVE ACTIVA: {n[2]} ({n[3]}) Nv.{n[4]}")
            except:
                pass
    
    texto = "TUS NAVES:\n\n"
    for n in naves:
        activa = " (ACTIVA)" if n[0] == activa_id else ""
        texto += f"{n[2]} - {n[3]} Nv.{n[4]}{activa}\n"
        texto += f"  Escudo: {n[5]} | Armas: {n[7]} | Bodega: {n[8]}\n\n"
    
    teclado = InlineKeyboardMarkup([[InlineKeyboardButton("Volver", callback_data="volver_nave")]])
    await context.bot.send_message(chat_id=user_id, text=texto, reply_markup=teclado)

async def comprar_nave_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    conn = sqlite3.connect('estelar.db')
    c = conn.cursor()
    c.execute("SELECT oro FROM personajes WHERE user_id=?", (user_id,))
    p = c.fetchone()
    conn.close()
    oro = p[0]
    teclado = []
    for tipo, datos in TIPOS_NAVE.items():
        teclado.append([InlineKeyboardButton(f"{datos['nombre']} - {datos['costo']} oro", callback_data=f"comprar_{tipo}")])
    teclado.append([InlineKeyboardButton("Volver", callback_data="volver_nave")])
    await query.edit_message_text(f"CONCESIONARIO\n\nTu oro: {oro}", reply_markup=InlineKeyboardMarkup(teclado))

async def comprar_nave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    tipo = query.data.replace("comprar_", "")
    if tipo not in TIPOS_NAVE:
        return
    datos = TIPOS_NAVE[tipo]
    conn = sqlite3.connect('estelar.db')
    c = conn.cursor()
    c.execute("SELECT oro, nave_activa FROM personajes WHERE user_id=?", (user_id,))
    p = c.fetchone()
    oro = p[0]
    if oro < datos["costo"]:
        conn.close()
        await query.edit_message_text("No tienes suficiente oro.")
        return
    c.execute("UPDATE personajes SET oro = oro - ? WHERE user_id=?", (datos["costo"], user_id))
    nombre_nave = f"Nave de {query.from_user.first_name}"
    c.execute("INSERT INTO naves (dueno_id, nombre, tipo, escudo, blindaje, armas, bodega, costo) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
              (user_id, nombre_nave, tipo, datos["escudo"], datos["blindaje"], datos["armas"], datos["bodega"], datos["costo"]))
    nave_id = c.lastrowid
    if p[1] == 0:
        c.execute("UPDATE personajes SET nave_activa = ? WHERE user_id=?", (nave_id, user_id))
        msg = "\nNave activada automaticamente."
    else:
        msg = ""
    conn.commit()
    conn.close()
    
    try:
        with open(f"img/naves/{tipo}.jpg", "rb") as foto:
            await context.bot.send_photo(chat_id=user_id, photo=foto, caption=f"Compra exitosa!\n\n{datos['nombre']} {nombre_nave}\nEscudo: {datos['escudo']}\nArmas: {datos['armas']}\nBodega: {datos['bodega']}\nOro restante: {oro - datos['costo']}{msg}")
    except:
        pass
    
    teclado = InlineKeyboardMarkup([[InlineKeyboardButton("Volver al menu", callback_data="volver_start")]])
    await query.edit_message_text(f"Compra exitosa!\n{datos['nombre']} {nombre_nave}\nOro restante: {oro - datos['costo']}{msg}", reply_markup=teclado)

async def seleccionar_nave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    conn = sqlite3.connect('estelar.db')
    c = conn.cursor()
    c.execute("SELECT id, nombre, tipo FROM naves WHERE dueno_id=?", (user_id,))
    naves = c.fetchall()
    conn.close()
    if not naves:
        await query.edit_message_text("No tienes naves.")
        return
    teclado = []
    for n in naves:
        teclado.append([InlineKeyboardButton(f"{n[2]} - {n[1]}", callback_data=f"activar_{n[0]}")])
    teclado.append([InlineKeyboardButton("Volver", callback_data="volver_nave")])
    await query.edit_message_text("Selecciona la nave a activar:", reply_markup=InlineKeyboardMarkup(teclado))

async def activar_nave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    nave_id = int(query.data.replace("activar_", ""))
    conn = sqlite3.connect('estelar.db')
    c = conn.cursor()
    c.execute("SELECT * FROM naves WHERE id=? AND dueno_id=?", (nave_id, user_id))
    if not c.fetchone():
        conn.close()
        await query.edit_message_text("Esa nave no es tuya.")
        return
    c.execute("UPDATE personajes SET nave_activa = ? WHERE user_id=?", (nave_id, user_id))
    conn.commit()
    c.execute("SELECT nombre, tipo FROM naves WHERE id=?", (nave_id,))
    nave = c.fetchone()
    conn.close()
    teclado = InlineKeyboardMarkup([[InlineKeyboardButton("Volver al menu", callback_data="volver_start")]])
    await query.edit_message_text(f"Nave activada: {nave[0]} ({nave[1]})", reply_markup=teclado)

async def volver_nave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await nave_menu(update, context)
async def nave_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        mensaje = query.edit_message_text
    else:
        user_id = update.message.from_user.id
        mensaje = update.message.reply_text
    
    conn = sqlite3.connect('estelar.db')
    c = conn.cursor()
    c.execute("SELECT * FROM personajes WHERE user_id=?", (user_id,))
    p = c.fetchone()
    if not p:
        conn.close()
        await mensaje("Primero crea tu personaje.")
        return
    c.execute("SELECT * FROM naves WHERE dueno_id=?", (user_id,))
    naves = c.fetchall()
    conn.close()
    
    teclado = []
    if naves:
        teclado.append([InlineKeyboardButton("Ver mis naves", callback_data="ver_naves")])
        teclado.append([InlineKeyboardButton("Seleccionar nave activa", callback_data="sel_nave")])
    teclado.append([InlineKeyboardButton("Comprar nave", callback_data="comprar_nave")])
    teclado.append([InlineKeyboardButton("Volver al menu", callback_data="volver_start")])
    
    await mensaje(f"GESTION DE NAVES\n\nTu oro: {p[5]}\nNaves: {len(naves)}", reply_markup=InlineKeyboardMarkup(teclado))

async def ver_naves(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    conn = sqlite3.connect('estelar.db')
    c = conn.cursor()
    c.execute("SELECT nave_activa FROM personajes WHERE user_id=?", (user_id,))
    activa_id = c.fetchone()[0]
    c.execute("SELECT * FROM naves WHERE dueno_id=?", (user_id,))
    naves = c.fetchall()
    conn.close()
    if not naves:
        await query.edit_message_text("No tienes naves.")
        return
    
    for n in naves:
        if n[0] == activa_id:
            try:
                with open(f"img/naves/{n[3]}.jpg", "rb") as foto:
                    await context.bot.send_photo(chat_id=user_id, photo=foto, caption=f"NAVE ACTIVA: {n[2]} ({n[3]}) Nv.{n[4]}")
            except:
                pass
    
    texto = "TUS NAVES:\n\n"
    for n in naves:
        activa = " (ACTIVA)" if n[0] == activa_id else ""
        texto += f"{n[2]} - {n[3]} Nv.{n[4]}{activa}\n"
        texto += f"  Escudo: {n[5]} | Armas: {n[7]} | Bodega: {n[8]}\n\n"
    
    teclado = InlineKeyboardMarkup([[InlineKeyboardButton("Volver", callback_data="volver_nave")]])
    await context.bot.send_message(chat_id=user_id, text=texto, reply_markup=teclado)

async def comprar_nave_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    conn = sqlite3.connect('estelar.db')
    c = conn.cursor()
    c.execute("SELECT oro FROM personajes WHERE user_id=?", (user_id,))
    p = c.fetchone()
    conn.close()
    oro = p[0]
    teclado = []
    for tipo, datos in TIPOS_NAVE.items():
        teclado.append([InlineKeyboardButton(f"{datos['nombre']} - {datos['costo']} oro", callback_data=f"comprar_{tipo}")])
    teclado.append([InlineKeyboardButton("Volver", callback_data="volver_nave")])
    await query.edit_message_text(f"CONCESIONARIO\n\nTu oro: {oro}", reply_markup=InlineKeyboardMarkup(teclado))

async def comprar_nave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    tipo = query.data.replace("comprar_", "")
    if tipo not in TIPOS_NAVE:
        return
    datos = TIPOS_NAVE[tipo]
    conn = sqlite3.connect('estelar.db')
    c = conn.cursor()
    c.execute("SELECT oro, nave_activa FROM personajes WHERE user_id=?", (user_id,))
    p = c.fetchone()
    oro = p[0]
    if oro < datos["costo"]:
        conn.close()
        await query.edit_message_text("No tienes suficiente oro.")
        return
    c.execute("UPDATE personajes SET oro = oro - ? WHERE user_id=?", (datos["costo"], user_id))
    nombre_nave = f"Nave de {query.from_user.first_name}"
    c.execute("INSERT INTO naves (dueno_id, nombre, tipo, escudo, blindaje, armas, bodega, costo) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
              (user_id, nombre_nave, tipo, datos["escudo"], datos["blindaje"], datos["armas"], datos["bodega"], datos["costo"]))
    nave_id = c.lastrowid
    if p[1] == 0:
        c.execute("UPDATE personajes SET nave_activa = ? WHERE user_id=?", (nave_id, user_id))
        msg = "\nNave activada automaticamente."
    else:
        msg = ""
    conn.commit()
    conn.close()
    
    try:
        with open(f"img/naves/{tipo}.jpg", "rb") as foto:
            await context.bot.send_photo(chat_id=user_id, photo=foto, caption=f"Compra exitosa!\n\n{datos['nombre']} {nombre_nave}\nEscudo: {datos['escudo']}\nArmas: {datos['armas']}\nBodega: {datos['bodega']}\nOro restante: {oro - datos['costo']}{msg}")
    except:
        pass
    
    teclado = InlineKeyboardMarkup([[InlineKeyboardButton("Volver al menu", callback_data="volver_start")]])
    await query.edit_message_text(f"Compra exitosa!\n{datos['nombre']} {nombre_nave}\nOro restante: {oro - datos['costo']}{msg}", reply_markup=teclado)

async def seleccionar_nave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    conn = sqlite3.connect('estelar.db')
    c = conn.cursor()
    c.execute("SELECT id, nombre, tipo FROM naves WHERE dueno_id=?", (user_id,))
    naves = c.fetchall()
    conn.close()
    if not naves:
        await query.edit_message_text("No tienes naves.")
        return
    teclado = []
    for n in naves:
        teclado.append([InlineKeyboardButton(f"{n[2]} - {n[1]}", callback_data=f"activar_{n[0]}")])
    teclado.append([InlineKeyboardButton("Volver", callback_data="volver_nave")])
    await query.edit_message_text("Selecciona la nave a activar:", reply_markup=InlineKeyboardMarkup(teclado))

async def activar_nave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    nave_id = int(query.data.replace("activar_", ""))
    conn = sqlite3.connect('estelar.db')
    c = conn.cursor()
    c.execute("SELECT * FROM naves WHERE id=? AND dueno_id=?", (nave_id, user_id))
    if not c.fetchone():
        conn.close()
        await query.edit_message_text("Esa nave no es tuya.")
        return
    c.execute("UPDATE personajes SET nave_activa = ? WHERE user_id=?", (nave_id, user_id))
    conn.commit()
    c.execute("SELECT nombre, tipo FROM naves WHERE id=?", (nave_id,))
    nave = c.fetchone()
    conn.close()
    teclado = InlineKeyboardMarkup([[InlineKeyboardButton("Volver al menu", callback_data="volver_start")]])
    await query.edit_message_text(f"Nave activada: {nave[0]} ({nave[1]})", reply_markup=teclado)

async def volver_nave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await nave_menu(update, context)
# ============ SISTEMA DE STATS DE PERSONAJE ============

STATS_BASE = {
    "piloto": {"precision": 5, "defensa": 5, "extraccion": 5, "velocidad": 10, "suerte": 5},
    "armero": {"precision": 10, "defensa": 10, "extraccion": 5, "velocidad": 5, "suerte": 5},
    "minero": {"precision": 5, "defensa": 5, "extraccion": 10, "velocidad": 5, "suerte": 5}
}

def obtener_stats_jugador(user_id):
    """Devuelve los stats de un jugador"""
    conn = sqlite3.connect('estelar.db')
    c = conn.cursor()
    
    c.execute("SELECT oficio, nivel FROM personajes WHERE user_id=?", (user_id,))
    p = c.fetchone()
    if not p:
        conn.close()
        return None
    
    c.execute("SELECT * FROM stats_personaje WHERE user_id=?", (user_id,))
    s = c.fetchone()
    
    if not s:
        base = STATS_BASE.get(p[0], STATS_BASE["piloto"])
        conn.close()
        return {
            "precision": base["precision"] + p[1] * 2,
            "defensa": base["defensa"] + p[1] * 2,
            "extraccion": base["extraccion"] + p[1] * 2,
            "velocidad": base["velocidad"] + p[1] * 2,
            "suerte": base["suerte"] + p[1] * 2,
        }
    
    conn.close()
    return {
        "precision": s[1],
        "defensa": s[2],
        "extraccion": s[3],
        "velocidad": s[4],
        "suerte": s[5],
    }

def obtener_stats_tripulacion(nave_id, capitan_id):
    """Devuelve los stats combinados de toda la tripulación de una nave"""
    conn = sqlite3.connect('estelar.db')
    c = conn.cursor()
    
    stats_total = {"precision": 0, "defensa": 0, "extraccion": 0, "velocidad": 0, "suerte": 0}
    nombres = []
    
    # Stats del capitán
    c.execute("SELECT oficio, nivel FROM personajes WHERE user_id=?", (capitan_id,))
    cap = c.fetchone()
    if cap:
        c.execute("SELECT * FROM stats_personaje WHERE user_id=?", (capitan_id,))
        s = c.fetchone()
        if s:
            stats_total["precision"] += s[1]
            stats_total["defensa"] += s[2]
            stats_total["extraccion"] += s[3]
            stats_total["velocidad"] += s[4]
            stats_total["suerte"] += s[5]
        else:
            base = STATS_BASE.get(cap[0], STATS_BASE["piloto"])
            stats_total["precision"] += base["precision"] + cap[1] * 2
            stats_total["defensa"] += base["defensa"] + cap[1] * 2
            stats_total["extraccion"] += base["extraccion"] + cap[1] * 2
            stats_total["velocidad"] += base["velocidad"] + cap[1] * 2
            stats_total["suerte"] += base["suerte"] + cap[1] * 2
        c.execute("SELECT nombre FROM personajes WHERE user_id=?", (capitan_id,))
        nom = c.fetchone()
        nombres.append(f"{nom[0]} (Capitán)")
    
    # Stats de tripulantes
    c.execute("SELECT user_id, oficio FROM tripulacion WHERE nave_id=?", (nave_id,))
    tripulantes = c.fetchall()
    
    for t in tripulantes:
        c.execute("SELECT * FROM stats_personaje WHERE user_id=?", (t[0],))
        s = c.fetchone()
        if s:
            stats_total["precision"] += s[1]
            stats_total["defensa"] += s[2]
            stats_total["extraccion"] += s[3]
            stats_total["velocidad"] += s[4]
            stats_total["suerte"] += s[5]
        else:
            base = STATS_BASE.get(t[1], STATS_BASE["piloto"])
            c.execute("SELECT nivel FROM personajes WHERE user_id=?", (t[0],))
            niv = c.fetchone()
            nivel = niv[0] if niv else 1
            stats_total["precision"] += base["precision"] + nivel * 2
            stats_total["defensa"] += base["defensa"] + nivel * 2
            stats_total["extraccion"] += base["extraccion"] + nivel * 2
            stats_total["velocidad"] += base["velocidad"] + nivel * 2
            stats_total["suerte"] += base["suerte"] + nivel * 2
        c.execute("SELECT nombre FROM personajes WHERE user_id=?", (t[0],))
        nom = c.fetchone()
        if nom:
            nombres.append(f"{nom[0]} ({t[1]})")
    
    conn.close()
    
    return {
        "stats": stats_total,
        "nombres": nombres,
        "bonus": {
            "exito": stats_total["precision"] // 5 + stats_total["suerte"] // 5,
            "defensa": stats_total["defensa"] // 5,
            "extraccion": stats_total["extraccion"] // 5,
            "velocidad": stats_total["velocidad"] // 5,
            "suerte": stats_total["suerte"] // 5
        }
    }

async def ver_stats_personaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        mensaje = query.edit_message_text
    else:
        user_id = update.message.from_user.id
        mensaje = update.message.reply_text
    
    conn = sqlite3.connect('estelar.db')
    c = conn.cursor()
    c.execute("SELECT * FROM personajes WHERE user_id=?", (user_id,))
    p = c.fetchone()
    if not p:
        conn.close()
        await mensaje("No tienes personaje.")
        return
    
    c.execute("SELECT * FROM stats_personaje WHERE user_id=?", (user_id,))
    s = c.fetchone()
    
    if not s:
        base = STATS_BASE.get(p[2], STATS_BASE["piloto"])
        c.execute("INSERT INTO stats_personaje (user_id, precision, defensa, extraccion, velocidad, suerte) VALUES (?, ?, ?, ?, ?, ?)",
                  (user_id, base["precision"], base["defensa"], base["extraccion"], base["velocidad"], base["suerte"]))
        conn.commit()
        c.execute("SELECT * FROM stats_personaje WHERE user_id=?", (user_id,))
        s = c.fetchone()
    
    puntos = s[6]
    conn.close()
    
    texto = f"📊 STATS DE {p[1].upper()}\n"
    texto += f"Oficio: {p[2].capitalize()} | Nivel: {p[3]}\n\n"
    texto += f"🎯 Precisión: {s[1]}\n"
    texto += f"🛡️ Defensa: {s[2]}\n"
    texto += f"⛏️ Extracción: {s[3]}\n"
    texto += f"🚀 Velocidad: {s[4]}\n"
    texto += f"🍀 Suerte: {s[5]}\n"
    
    if puntos > 0:
        texto += f"\n⭐ Puntos libres: {puntos}\n"
    
    teclado = []
    if puntos > 0:
        for stat in ["precision", "defensa", "extraccion", "velocidad", "suerte"]:
            teclado.append([InlineKeyboardButton(
                f"Mejorar {stat.capitalize()} (+1)",
                callback_data=f"mejorar_{stat}"
            )])
    
    teclado.append([InlineKeyboardButton("Volver al menu", callback_data="volver_start")])
    
    await mensaje(texto, reply_markup=InlineKeyboardMarkup(teclado))

async def mejorar_stat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    stat = query.data.replace("mejorar_", "")
    
    if stat not in ["precision", "defensa", "extraccion", "velocidad", "suerte"]:
        return
    
    conn = sqlite3.connect('estelar.db')
    c = conn.cursor()
    c.execute("SELECT * FROM stats_personaje WHERE user_id=?", (user_id,))
    s = c.fetchone()
    
    if not s:
        conn.close()
        await query.edit_message_text("No tienes stats.")
        return
    
    puntos = s[6]
    if puntos <= 0:
        conn.close()
        await query.edit_message_text("No tienes puntos libres. Sube de nivel para conseguirlos.")
        return
    
    c.execute(f"UPDATE stats_personaje SET {stat} = {stat} + 1, puntos_libres = puntos_libres - 1 WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()
    
    await query.answer(f"{stat.capitalize()} mejorado!")
    await ver_stats_personaje(update, context)
# ============ SISTEMA DE EXPEDICIONES ============
import random
import asyncio
from datetime import datetime

EXPEDICIONES_ACTIVAS = {}

SECTORES = {
    "high": {
        "nombre": "High Sec",
        "emoji": "🟢",
        "multiplicador": 1,
        "riesgo": "Bajo",
        "pvp": False,
        "porcentaje_est": 0.10,
        "prob_exito": 95,
        "prob_evento": 20,
        "riesgo_nave": 0
    },
    "low": {
        "nombre": "Low Sec",
        "emoji": "🟡",
        "multiplicador": 2,
        "riesgo": "Medio",
        "pvp": "posible",
        "porcentaje_est": 0.25,
        "prob_exito": 80,
        "prob_evento": 40,
        "riesgo_nave": 5
    },
    "null": {
        "nombre": "Null Sec",
        "emoji": "🔴",
        "multiplicador": 4,
        "riesgo": "Alto",
        "pvp": True,
        "porcentaje_est": 0.50,
        "prob_exito": 60,
        "prob_evento": 60,
        "riesgo_nave": 15
    }
}

TIPOS_EXPEDICION = {
    "exploracion": {
        "nombre": "Exploracion",
        "requiere": ["piloto"],
        "duracion": 30,
        "oro_base_min": 30,
        "oro_base_max": 80,
        "exp_base": 10,
        "minerales": False,
        "costo_base": 10
    },
    "mineria": {
        "nombre": "Mineria",
        "requiere": ["piloto", "minero"],
        "duracion": 45,
        "oro_base_min": 20,
        "oro_base_max": 50,
        "exp_base": 25,
        "minerales": True,
        "costo_base": 25
    },
    "combate": {
        "nombre": "Combate PvE",
        "requiere": ["piloto", "armero"],
        "duracion": 40,
        "oro_base_min": 50,
        "oro_base_max": 150,
        "exp_base": 40,
        "minerales": False,
        "costo_base": 40
    },
    "gran_expedicion": {
        "nombre": "Gran Expedicion",
        "requiere": ["piloto", "armero", "minero"],
        "duracion": 60,
        "oro_base_min": 100,
        "oro_base_max": 300,
        "exp_base": 80,
        "minerales": True,
        "costo_base": 80
    }
}

EVENTOS = {
    "tesoro": {"nombre": "💎 Tesoro Oculto", "oro_extra": 50, "msg": "Has encontrado un cofre flotante con oro!"},
    "piratas": {"nombre": "🏴‍☠️ Ataque Pirata", "oro_perdida": 30, "msg": "Piratas te han emboscado y robado parte del botin!"},
    "averia": {"nombre": "🔧 Averia Tecnica", "dano": 15, "msg": "Un fallo en el motor ha causado daños en la nave!"},
    "estelio": {"nombre": "💎 Veta de Estelio", "est_extra": 10, "msg": "Has encontrado una veta pura de Estelio!"},
    "alien": {"nombre": "👽 Encuentro Alien", "exp_extra": 20, "msg": "Una especie alienigena te ha bendecido con conocimiento!"},
    "tormenta": {"nombre": "🌌 Tormenta Espacial", "duracion_extra": 15, "msg": "Una tormenta ionica retrasa tu expedicion!"}
}

EXPEDICIONES_RARAS = {
    "caza_recompensa": {
        "nombre": "🎯 Caza de Recompensa",
        "requiere": ["piloto", "armero"],
        "duracion": 90,
        "oro_base_min": 200,
        "oro_base_max": 500,
        "exp_base": 100,
        "minerales": False,
        "costo_base": 100,
        "prob_aparicion": 10
    },
    "asteroide_legendario": {
        "nombre": "☄️ Asteroide Legendario",
        "requiere": ["piloto", "minero"],
        "duracion": 120,
        "oro_base_min": 300,
        "oro_base_max": 800,
        "exp_base": 150,
        "minerales": True,
        "costo_base": 150,
        "prob_aparicion": 8
    }
}

async def expedicion_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        mensaje = query.edit_message_text
    else:
        user_id = update.message.from_user.id
        mensaje = update.message.reply_text
    
    if user_id in EXPEDICIONES_ACTIVAS:
        exp = EXPEDICIONES_ACTIVAS[user_id]
        restante = exp["fin"] - datetime.now()
        segundos = int(restante.total_seconds())
        if segundos <= 0:
            EXPEDICIONES_ACTIVAS.pop(user_id)
        else:
            sector = SECTORES[exp["sector"]]
            teclado = InlineKeyboardMarkup([
                [InlineKeyboardButton("Cancelar expedicion", callback_data="cancelar_exp")],
                [InlineKeyboardButton("Volver al menu", callback_data="volver_start")]
            ])
            await mensaje(
                f"{sector['emoji']} EXPEDICION EN CURSO\n\n"
                f"Sector: {sector['nombre']}\n"
                f"Tipo: {exp['tipo_nombre']}\n"
                f"Tiempo restante: {segundos} segundos\n"
                f"Riesgo: {sector['riesgo']}\n"
                f"Prob. exito: {exp.get('prob_exito', 80)}%\n\n"
                f"Espera a que termine...",
                reply_markup=teclado
            )
            return
    
    conn = sqlite3.connect('estelar.db')
    c = conn.cursor()
    c.execute("SELECT * FROM personajes WHERE user_id=?", (user_id,))
    p = c.fetchone()
    if not p:
        conn.close()
        await mensaje("No tienes personaje.")
        return
    if p[6] == 0:
        conn.close()
        await mensaje("No tienes nave activa.")
        return
    
    nave_id = p[6]
    mi_oficio = p[2]
    
    c.execute("SELECT oficio FROM tripulacion WHERE nave_id=?", (nave_id,))
    tripulantes = [row[0] for row in c.fetchall()]
    tripulantes.append(mi_oficio)
    
    # Bonus por tripulación completa
    trip_completa = set(tripulantes) == {"piloto", "armero", "minero"}
    
    c.execute("SELECT nombre, tipo FROM naves WHERE id=?", (nave_id,))
    nave = c.fetchone()
    
    # Ver daño de la nave
    c.execute("SELECT dano FROM naves_dano WHERE nave_id=?", (nave_id,))
    dano_row = c.fetchone()
    dano = dano_row[0] if dano_row else 0
    
    # Ver racha
    c.execute("SELECT racha_actual FROM estadisticas WHERE user_id=?", (user_id,))
    racha_row = c.fetchone()
    racha = racha_row[0] if racha_row else 0
    
    conn.close()
    
    texto = f"🚀 EXPEDICIONES\n\n"
    texto += f"Nave: {nave[0]} ({nave[1]})\n"
    texto += f"Daño nave: {dano}%\n"
    texto += f"Tripulantes: {len(tripulantes)}/3\n"
    if trip_completa:
        texto += "🔥 Bonus tripulacion completa: +20% recompensas\n"
    if racha > 1:
        texto += f"🔥 Racha x{racha}: +{racha*5}% recompensas\n"
    texto += "\nSELECCIONA SECTOR:\n\n"
    
    teclado = []
    for sector_id, sector in SECTORES.items():
        mult = sector["multiplicador"]
        est_pct = int(sector["porcentaje_est"] * 100)
        texto += f"{sector['emoji']} {sector['nombre']}\n"
        texto += f"   Bonus: x{mult} | EST: {est_pct}% | Exito: {sector['prob_exito']}%\n"
        texto += f"   Riesgo nave: {sector['riesgo_nave']}%\n\n"
        teclado.append([InlineKeyboardButton(
            f"{sector['emoji']} {sector['nombre']} (x{mult}, {est_pct}% EST)",
            callback_data=f"sector_{sector_id}"
        )])
    
    # Verificar si aparece expedición rara
    for id_rara, datos_rara in EXPEDICIONES_RARAS.items():
        if random.randint(1, 100) <= datos_rara["prob_aparicion"]:
            texto += f"\n🌟 EXPEDICION RARA DISPONIBLE:\n"
            texto += f"{datos_rara['nombre']}\n"
            texto += f"   Premio: {datos_rara['oro_base_min']}-{datos_rara['oro_base_max']} oro\n\n"
            teclado.append([InlineKeyboardButton(
                f"🌟 {datos_rara['nombre']}",
                callback_data=f"rara_{id_rara}"
            )])
    
    teclado.append([InlineKeyboardButton("📊 Estadisticas", callback_data="menu_stats_exp")])
    teclado.append([InlineKeyboardButton("Volver al menu", callback_data="volver_start")])
    
    await mensaje(texto, reply_markup=InlineKeyboardMarkup(teclado))

async def elegir_expedicion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    sector_id = query.data.replace("sector_", "")
    
    if sector_id not in SECTORES:
        return
    
    context.user_data["sector_elegido"] = sector_id
    sector = SECTORES[sector_id]
    
    conn = sqlite3.connect('estelar.db')
    c = conn.cursor()
    c.execute("SELECT oficio, nave_activa FROM personajes WHERE user_id=?", (user_id,))
    p = c.fetchone()
    mi_oficio = p[0]
    nave_id = p[1]
    
    c.execute("SELECT oficio FROM tripulacion WHERE nave_id=?", (nave_id,))
    tripulantes = [row[0] for row in c.fetchall()]
    tripulantes.append(mi_oficio)
    
    trip_completa = set(tripulantes) == {"piloto", "armero", "minero"}
    
    c.execute("SELECT nombre, tipo FROM naves WHERE id=?", (nave_id,))
    nave = c.fetchone()
    
    c.execute("SELECT racha_actual FROM estadisticas WHERE user_id=?", (user_id,))
    racha_row = c.fetchone()
    racha = racha_row[0] if racha_row else 0
    conn.close()
    
    texto = f"{sector['emoji']} {sector['nombre']} - EXPEDICIONES\n\n"
    texto += f"Nave: {nave[0]} ({nave[1]})\n"
    texto += f"Bonus sector: x{sector['multiplicador']} | EST: {int(sector['porcentaje_est']*100)}%\n"
    if trip_completa:
        texto += "🔥 Tripulacion completa: +20%\n"
    if racha > 1:
        texto += f"🔥 Racha x{racha}: +{racha*5}%\n"
    texto += "\nExpediciones disponibles:\n\n"
    
    teclado = []
    for tipo, datos in TIPOS_EXPEDICION.items():
        req = datos["requiere"]
        disponible = all(r in tripulantes for r in req)
        
        oro_min = datos["oro_base_min"] * sector["multiplicador"]
        oro_max = datos["oro_base_max"] * sector["multiplicador"]
        exp = datos["exp_base"] * sector["multiplicador"]
        est = round(oro_min * sector["porcentaje_est"], 1)
        costo = datos["costo_base"] * sector["multiplicador"]
        
        if trip_completa:
            oro_min = int(oro_min * 1.2)
            oro_max = int(oro_max * 1.2)
        if racha > 1:
            oro_min = int(oro_min * (1 + racha * 0.05))
            oro_max = int(oro_max * (1 + racha * 0.05))
        
        icono = "✅" if disponible else "❌"
        texto += f"{icono} {datos['nombre']}\n"
        texto += f"   Requiere: {', '.join(req)}\n"
        texto += f"   Costo: {costo} oro\n"
        texto += f"   Recompensa: {oro_min}-{oro_max} oro\n"
        texto += f"   EXP: {exp} | EST: ~{est}\n"
        texto += f"   Duracion: {datos['duracion']}s\n\n"
        
        if disponible:
            teclado.append([InlineKeyboardButton(
                f"{datos['nombre']} - Costo:{costo} | Premio:{oro_min}-{oro_max}",
                callback_data=f"exp_{tipo}"
            )])
    
    teclado.append([InlineKeyboardButton("Volver a sectores", callback_data="menu_exp")])
    
    await query.edit_message_text(texto, reply_markup=InlineKeyboardMarkup(teclado))

async def iniciar_expedicion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    tipo = query.data.replace("exp_", "")
    
    if tipo not in TIPOS_EXPEDICION:
        return
    
    if user_id in EXPEDICIONES_ACTIVAS:
        await query.edit_message_text("Ya tienes una expedicion en curso.")
        return
    
    sector_id = context.user_data.get("sector_elegido", "high")
    sector = SECTORES[sector_id]
    datos = TIPOS_EXPEDICION[tipo]
    
    costo = datos["costo_base"] * sector["multiplicador"]
    
    conn = sqlite3.connect('estelar.db')
    c = conn.cursor()
    c.execute("SELECT oficio, nave_activa, oro FROM personajes WHERE user_id=?", (user_id,))
    p = c.fetchone()
    mi_oficio = p[0]
    nave_id = p[1]
    oro_actual = p[2]
    
    c.execute("SELECT oficio FROM tripulacion WHERE nave_id=?", (nave_id,))
    tripulantes = [row[0] for row in c.fetchall()]
    tripulantes.append(mi_oficio)
    
    trip_completa = set(tripulantes) == {"piloto", "armero", "minero"}
    
    if not all(r in tripulantes for r in datos["requiere"]):
        conn.close()
        await query.edit_message_text("No tienes la tripulacion necesaria.")
        return
    
    if oro_actual < costo:
        conn.close()
        await query.edit_message_text(f"No tienes suficiente oro.\nNecesitas: {costo} oro\nTienes: {oro_actual} oro")
        return
    
    # Ver daño de la nave
    c.execute("SELECT dano FROM naves_dano WHERE nave_id=?", (nave_id,))
    dano_row = c.fetchone()
    dano = dano_row[0] if dano_row else 0
    
    # Probabilidad de éxito reducida por daño
    prob_exito = sector["prob_exito"] - (dano // 10) * 5
    if prob_exito < 10:
        prob_exito = 10
    
    c.execute("SELECT racha_actual FROM estadisticas WHERE user_id=?", (user_id,))
    racha_row = c.fetchone()
    racha = racha_row[0] if racha_row else 0
    
    # Cobrar el costo
    c.execute("UPDATE personajes SET oro = oro - ? WHERE user_id=?", (costo, user_id))
    
    # Inicializar estadisticas si no existen
    c.execute("SELECT * FROM estadisticas WHERE user_id=?", (user_id,))
    if not c.fetchone():
        c.execute("INSERT INTO estadisticas (user_id) VALUES (?)", (user_id,))
    
    conn.commit()
    conn.close()
    
    duracion = datos["duracion"]
    fin = datetime.now().timestamp() + duracion
    
    EXPEDICIONES_ACTIVAS[user_id] = {
        "tipo": tipo,
        "tipo_nombre": datos["nombre"],
        "sector": sector_id,
        "fin": datetime.fromtimestamp(fin),
        "oro_base_min": datos["oro_base_min"],
        "oro_base_max": datos["oro_base_max"],
        "exp_base": datos["exp_base"],
        "multiplicador": sector["multiplicador"],
        "porcentaje_est": sector["porcentaje_est"],
        "minerales": datos["minerales"],
        "prob_exito": prob_exito,
        "trip_completa": trip_completa,
        "racha": racha,
        "riesgo_nave": sector["riesgo_nave"]
    }
    
    oro_min = datos["oro_base_min"] * sector["multiplicador"]
    oro_max = datos["oro_base_max"] * sector["multiplicador"]
    
    if trip_completa:
        oro_min = int(oro_min * 1.2)
        oro_max = int(oro_max * 1.2)
    if racha > 1:
        oro_min = int(oro_min * (1 + racha * 0.05))
        oro_max = int(oro_max * (1 + racha * 0.05))
    
    est_pct = int(sector["porcentaje_est"] * 100)
    
    await query.edit_message_text(
        f"{sector['emoji']} EXPEDICION INICIADA\n\n"
        f"Sector: {sector['nombre']}\n"
        f"Tipo: {datos['nombre']}\n"
        f"Costo pagado: {costo} oro\n"
        f"Duracion: {duracion} segundos\n"
        f"Prob. exito: {prob_exito}%\n"
        f"Recompensa posible: {oro_min}-{oro_max} oro\n"
        f"EXP: {datos['exp_base']} | EST: {est_pct}% del oro\n\n"
        f"Te notificare cuando termine.\n"
        f"Usa /expedicion para ver el progreso."
    )
    
    asyncio.create_task(finalizar_expedicion(user_id, tipo, context))

async def iniciar_expedicion_rara(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    tipo = query.data.replace("rara_", "")
    
    if tipo not in EXPEDICIONES_RARAS:
        return
    
    if user_id in EXPEDICIONES_ACTIVAS:
        await query.edit_message_text("Ya tienes una expedicion en curso.")
        return
    
    sector_id = context.user_data.get("sector_elegido", "high")
    sector = SECTORES[sector_id]
    datos = EXPEDICIONES_RARAS[tipo]
    
    costo = datos["costo_base"] * sector["multiplicador"]
    
    conn = sqlite3.connect('estelar.db')
    c = conn.cursor()
    c.execute("SELECT oficio, nave_activa, oro FROM personajes WHERE user_id=?", (user_id,))
    p = c.fetchone()
    mi_oficio = p[0]
    nave_id = p[1]
    oro_actual = p[2]
    
    c.execute("SELECT oficio FROM tripulacion WHERE nave_id=?", (nave_id,))
    tripulantes = [row[0] for row in c.fetchall()]
    tripulantes.append(mi_oficio)
    
    trip_completa = set(tripulantes) == {"piloto", "armero", "minero"}
    
    if not all(r in tripulantes for r in datos["requiere"]):
        conn.close()
        await query.edit_message_text("No tienes la tripulacion necesaria.")
        return
    
    if oro_actual < costo:
        conn.close()
        await query.edit_message_text(f"No tienes suficiente oro. Necesitas: {costo}")
        return
    
    c.execute("SELECT dano FROM naves_dano WHERE nave_id=?", (nave_id,))
    dano_row = c.fetchone()
    dano = dano_row[0] if dano_row else 0
    
    prob_exito = sector["prob_exito"] + 10 - (dano // 10) * 5
    
    c.execute("SELECT racha_actual FROM estadisticas WHERE user_id=?", (user_id,))
    racha_row = c.fetchone()
    racha = racha_row[0] if racha_row else 0
    
    c.execute("UPDATE personajes SET oro = oro - ? WHERE user_id=?", (costo, user_id))
    
    c.execute("SELECT * FROM estadisticas WHERE user_id=?", (user_id,))
    if not c.fetchone():
        c.execute("INSERT INTO estadisticas (user_id) VALUES (?)", (user_id,))
    
    conn.commit()
    conn.close()
    
    duracion = datos["duracion"]
    fin = datetime.now().timestamp() + duracion
    
    EXPEDICIONES_ACTIVAS[user_id] = {
        "tipo": tipo,
        "tipo_nombre": datos["nombre"],
        "sector": sector_id,
        "fin": datetime.fromtimestamp(fin),
        "oro_base_min": datos["oro_base_min"],
        "oro_base_max": datos["oro_base_max"],
        "exp_base": datos["exp_base"],
        "multiplicador": sector["multiplicador"],
        "porcentaje_est": sector["porcentaje_est"],
        "minerales": datos["minerales"],
        "prob_exito": prob_exito,
        "trip_completa": trip_completa,
        "racha": racha,
        "riesgo_nave": sector["riesgo_nave"] + 5,
        "es_rara": True
    }
    
    await query.edit_message_text(
        f"🌟 EXPEDICION RARA INICIADA\n\n"
        f"Sector: {sector['nombre']}\n"
        f"Tipo: {datos['nombre']}\n"
        f"Costo: {costo} oro\n"
        f"Duracion: {duracion} segundos\n"
        f"Recompensa: {datos['oro_base_min']}-{datos['oro_base_max']} oro\n\n"
        f"¡Esta es una oportunidad unica!"
    )
    
    asyncio.create_task(finalizar_expedicion(user_id, tipo, context))

async def finalizar_expedicion(user_id, tipo, context):
    if tipo in TIPOS_EXPEDICION:
        datos = TIPOS_EXPEDICION[tipo]
    elif tipo in EXPEDICIONES_RARAS:
        datos = EXPEDICIONES_RARAS[tipo]
    else:
        return

    await asyncio.sleep(datos["duracion"])

    if user_id not in EXPEDICIONES_ACTIVAS:
        return

    exp = EXPEDICIONES_ACTIVAS.pop(user_id)
    sector = SECTORES[exp["sector"]]

    tirada = random.randint(1, 100)
    exito = tirada <= exp["prob_exito"]
    nave_perdida = False

    conn = sqlite3.connect('estelar.db')
    c = conn.cursor()

    if exito:
        oro_ganado = random.randint(exp["oro_base_min"], exp["oro_base_max"]) * exp["multiplicador"]

        if exp["trip_completa"]:
            oro_ganado = int(oro_ganado * 1.2)
        if exp["racha"] > 1:
            oro_ganado = int(oro_ganado * (1 + exp["racha"] * 0.05))

        exp_ganada = exp["exp_base"] * exp["multiplicador"]
        est_ganados = round(oro_ganado * exp["porcentaje_est"], 2)

        evento_msg = ""
        if random.randint(1, 100) <= SECTORES[exp["sector"]]["prob_evento"]:
            evento = random.choice(list(EVENTOS.keys()))
            datos_evento = EVENTOS[evento]
            evento_msg = f"\n{datos_evento['msg']}"

            if "oro_extra" in datos_evento:
                oro_ganado += datos_evento["oro_extra"] * exp["multiplicador"]
            elif "oro_perdida" in datos_evento:
                oro_ganado = max(0, oro_ganado - datos_evento["oro_perdida"] * exp["multiplicador"])
            elif "est_extra" in datos_evento:
                est_ganados += datos_evento["est_extra"]
            elif "exp_extra" in datos_evento:
                exp_ganada += datos_evento["exp_extra"]
            elif "dano" in datos_evento:
                evento_msg += " La nave ha recibido daños!"

        c.execute("UPDATE personajes SET oro = oro + ?, experiencia = experiencia + ? WHERE user_id=?",
                  (oro_ganado, exp_ganada, user_id))

# Repartir botín: 50% dueño, 50% tripulación
        c.execute("SELECT nave_activa FROM personajes WHERE user_id=?", (user_id,))
        nav = c.fetchone()
        nave_id_actual = nav[0] if nav else 0

        c.execute("SELECT user_id FROM tripulacion WHERE nave_id=?", (nave_id_actual,))
        tripulantes_lista = c.fetchall()

        if tripulantes_lista:
                oro_dueno = int(oro_ganado * 0.5)
                oro_tripulante = int(oro_ganado * 0.5) // len(tripulantes_lista)
                exp_dueno = int(exp_ganada * 0.5)
                exp_tripulante = int(exp_ganada * 0.5) // len(tripulantes_lista)
        else:
            oro_dueno = oro_ganado
            oro_tripulante = 0
            exp_dueno = exp_ganada
            exp_tripulante = 0

# Dar oro y exp al dueño
        c.execute("UPDATE personajes SET oro = oro + ?, experiencia = experiencia + ? WHERE user_id=?",
        (oro_dueno, exp_dueno, user_id))

# Dar oro y exp a cada tripulante
        for t in tripulantes_lista:
            c.execute("UPDATE personajes SET oro = oro + ?, experiencia = experiencia + ? WHERE user_id=?",
              (oro_tripulante, exp_tripulante, t[0]))
            try:
                await context.bot.send_message(
                      chat_id=t[0],
            text=f"💰 BOTIN RECIBIDO\n\nHas recibido {oro_tripulante} oro y {exp_tripulante} EXP."
        )
            except:
                pass

# Subir nivel del dueño
        c.execute("SELECT experiencia, nivel FROM personajes WHERE user_id=?", (user_id,))
        p = c.fetchone()
        if p and p[0] >= p[1] * 100:
            c.execute("UPDATE personajes SET nivel = nivel + 1, experiencia = experiencia - ? WHERE user_id=?",
                      (p[1] * 100, user_id))
            c.execute("UPDATE stats_personaje SET puntos_libres = puntos_libres + 2 WHERE user_id=?", (user_id,))

# Subir nivel de tripulantes
        for t in tripulantes_lista:
            c.execute("SELECT experiencia, nivel FROM personajes WHERE user_id=?", (t[0],))
        pt = c.fetchone()
        if pt and pt[0] >= pt[1] * 100:
            c.execute("UPDATE personajes SET nivel = nivel + 1, experiencia = experiencia - ? WHERE user_id=?",
        (pt[1] * 100, t[0]))
        c.execute("UPDATE stats_personaje SET puntos_libres = puntos_libres + 2 WHERE user_id=?", (t[0],))
        minerales_texto = ""
        if exp["minerales"]:
            mineral = random.choice(["Hierro", "Cobre", "Titanio", "Cristal"])
            cantidad = random.randint(1, 5) * exp["multiplicador"]
            c.execute("SELECT * FROM inventario WHERE user_id=? AND recurso=?", (user_id, mineral))
            if c.fetchone():
                c.execute("UPDATE inventario SET cantidad = cantidad + ? WHERE user_id=? AND recurso=?", (cantidad, user_id, mineral))
            else:
                c.execute("INSERT INTO inventario (user_id, recurso, cantidad) VALUES (?, ?, ?)", (user_id, mineral, cantidad))
            minerales_texto = f"\nMinerales: {cantidad}x {mineral}"
        mensaje = (
            f"{sector['emoji']} EXPEDICION COMPLETADA ✅\n\n"
            f"Sector: {sector['nombre']}\n"
            f"Tipo: {exp['tipo_nombre']}\n"
            f"Oro total: {oro_ganado}\n"
            f"Tu parte (50%): {oro_dueno} oro | {exp_dueno} EXP\n"
            f"EST ganados: {est_ganados}{minerales_texto}"
            f"Tripulacion: {oro_tripulante} oro c/u | {exp_tripulante} EXP c/u\n"
            f"{evento_msg}\n\n"
            f"Usa /expedicion para otra mision!"
        )
        c.execute("SELECT * FROM tokens WHERE user_id=?", (user_id,))
        if c.fetchone():
            c.execute("UPDATE tokens SET balance = balance + ?, total_ganado = total_ganado + ? WHERE user_id=?",
                      (est_ganados, est_ganados, user_id))
        else:
            c.execute("INSERT INTO tokens (user_id, balance, total_ganado) VALUES (?, ?, ?)",
                      (user_id, est_ganados, est_ganados))

        c.execute("UPDATE estadisticas SET exp_completadas = exp_completadas + 1, racha_actual = racha_actual + 1, total_oro_ganado = total_oro_ganado + ?, total_est_ganado = total_est_ganado + ? WHERE user_id=?",
                  (oro_ganado, est_ganados, user_id))
        c.execute("UPDATE estadisticas SET mejor_racha = MAX(mejor_racha, racha_actual) WHERE user_id=? AND racha_actual > mejor_racha", (user_id,))

    else:
        c.execute("UPDATE estadisticas SET exp_falladas = exp_falladas + 1, racha_actual = 0 WHERE user_id=?", (user_id,))

        if random.randint(1, 100) <= exp["riesgo_nave"]:
            c.execute("SELECT nave_activa FROM personajes WHERE user_id=?", (user_id,))
            nav = c.fetchone()
            if nav and nav[0] > 0:
                c.execute("DELETE FROM naves WHERE id=?", (nav[0],))
                c.execute("UPDATE personajes SET nave_activa = 0 WHERE user_id=?", (user_id,))
                c.execute("UPDATE estadisticas SET naves_perdidas = naves_perdidas + 1 WHERE user_id=?", (user_id,))
                nave_perdida = True

        mensaje = (
            f"{sector['emoji']} EXPEDICION FRACASADA ❌\n\n"
            f"Sector: {sector['nombre']}\n"
            f"Tipo: {exp['tipo_nombre']}\n"
            f"La mision ha fallado. No obtienes recompensas.\n"
            f"Has perdido la racha de victorias."
        )
        if nave_perdida:
            mensaje += "\n\n💀 ¡HAS PERDIDO TU NAVE!"

    # Liberar tripulantes (SIEMPRE, al final)
    c.execute("SELECT nave_activa FROM personajes WHERE user_id=?", (user_id,))
    nav = c.fetchone()
    if nav and nav[0] > 0:
        nave_id_actual = nav[0]
        c.execute("SELECT user_id FROM tripulacion WHERE nave_id=?", (nave_id_actual,))
        tripulantes_ids = c.fetchall()
        for t in tripulantes_ids:
            try:
                await context.bot.send_message(
                    chat_id=t[0],
                    text="👥 CONTRATO FINALIZADO\n\n"
                    "La expedicion ha terminado y tu contrato ha finalizado.\n\n"
                    "Estas libre para unirte a otra tripulacion.\n"
                    "Usa /tablon para encontrar nuevas oportunidades."
                )
            except:
                pass
        c.execute("DELETE FROM tripulacion WHERE nave_id=?", (nave_id_actual,))

    conn.commit()
    conn.close()

    try:
        await context.bot.send_message(user_id, mensaje)
        await context.bot.send_message(
            user_id,
            "👥 ATENCION\n\n"
            "Los contratos de tu tripulacion han finalizado.\n"
            "Tus tripulantes han quedado libres.\n\n"
            "Publica un nuevo anuncio en el tablon para reclutar."
        )
    except:
        pass
async def estadisticas_exp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        mensaje = query.edit_message_text
    else:
        user_id = update.message.from_user.id
        mensaje = update.message.reply_text
    
    conn = sqlite3.connect('estelar.db')
    c = conn.cursor()
    c.execute("SELECT * FROM estadisticas WHERE user_id=?", (user_id,))
    e = c.fetchone()
    conn.close()
    
    if not e:
        teclado = InlineKeyboardMarkup([[InlineKeyboardButton("Volver", callback_data="menu_exp")]])
        await mensaje("No tienes estadisticas todavia.", reply_markup=teclado)
        return
    
    texto = (
        f"📊 ESTADISTICAS DE EXPEDICIONES\n\n"
        f"✅ Completadas: {e[1]}\n"
        f"❌ Falladas: {e[2]}\n"
        f"🔥 Racha actual: {e[3]}\n"
        f"🏆 Mejor racha: {e[4]}\n"
        f"💰 Total oro ganado: {e[5]}\n"
        f"🪙 Total EST ganado: {e[6]}\n"
        f"💀 Naves perdidas: {e[7]}\n"
    )
    
    if e[1] + e[2] > 0:
        tasa = round(e[1] / (e[1] + e[2]) * 100, 1)
        texto += f"\n📈 Tasa de exito: {tasa}%"
    
    teclado = InlineKeyboardMarkup([[InlineKeyboardButton("Volver a expediciones", callback_data="menu_exp")]])
    await mensaje(texto, reply_markup=teclado)

async def reparar_nave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        mensaje = query.edit_message_text
    else:
        user_id = update.message.from_user.id
        mensaje = update.message.reply_text
    
    conn = sqlite3.connect('estelar.db')
    c = conn.cursor()
    c.execute("SELECT nave_activa, oro FROM personajes WHERE user_id=?", (user_id,))
    p = c.fetchone()
    
    if not p or p[0] == 0:
        conn.close()
        await mensaje("No tienes nave activa.")
        return
    
    nave_id = p[0]
    oro = p[1]
    
    c.execute("SELECT dano FROM naves_dano WHERE nave_id=?", (nave_id,))
    dano_row = c.fetchone()
    dano = dano_row[0] if dano_row else 0
    
    if dano == 0:
        conn.close()
        await mensaje("Tu nave no tiene daños.")
        return
    
    costo_reparacion = dano * 5
    
    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton(f"Reparar ({costo_reparacion} oro)", callback_data="confirmar_reparar")],
        [InlineKeyboardButton("Volver", callback_data="volver_start")]
    ])
    
    conn.close()
    
    await mensaje(
        f"🔧 REPARAR NAVE\n\n"
        f"Daño actual: {dano}%\n"
        f"Costo reparacion: {costo_reparacion} oro\n"
        f"Tu oro: {oro}\n\n"
        f"Una nave dañada reduce la probabilidad de exito.",
        reply_markup=teclado
    )

async def confirmar_reparar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    conn = sqlite3.connect('estelar.db')
    c = conn.cursor()
    c.execute("SELECT nave_activa, oro FROM personajes WHERE user_id=?", (user_id,))
    p = c.fetchone()
    nave_id = p[0]
    oro = p[1]
    
    c.execute("SELECT dano FROM naves_dano WHERE nave_id=?", (nave_id,))
    dano_row = c.fetchone()
    dano = dano_row[0] if dano_row else 0
    
    costo = dano * 5
    
    if oro < costo:
        conn.close()
        await query.edit_message_text("No tienes suficiente oro.")
        return
    
    c.execute("UPDATE personajes SET oro = oro - ? WHERE user_id=?", (costo, user_id))
    c.execute("UPDATE naves_dano SET dano = 0 WHERE nave_id=?", (nave_id,))
    conn.commit()
    conn.close()
    
    await query.edit_message_text(
        f"✅ Nave reparada!\n\n"
        f"Daño: 0%\n"
        f"Oro gastado: {costo}\n"
        f"Oro restante: {oro - costo}"
    )

async def cancelar_expedicion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    if user_id in EXPEDICIONES_ACTIVAS:
        exp = EXPEDICIONES_ACTIVAS.pop(user_id)
        
        # Devolver 50% del costo (en este caso perdemos la info del costo original)
        # Como no guardamos el costo, solo cancelamos sin devolución
        conn = sqlite3.connect('estelar.db')
        c = conn.cursor()
        c.execute("UPDATE estadisticas SET exp_falladas = exp_falladas + 1, racha_actual = 0 WHERE user_id=?", (user_id,))
        conn.commit()
        conn.close()
        
        await query.edit_message_text("Expedicion cancelada. Has perdido la inversion y la racha.")
    else:
        await query.edit_message_text("No tienes expediciones activas.")
# ============ SISTEMA DE TOKENS EST ============

async def ver_tokens(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        mensaje = query.edit_message_text
    else:
        user_id = update.message.from_user.id
        mensaje = update.message.reply_text
    
    conn = sqlite3.connect('estelar.db')
    c = conn.cursor()
    c.execute("SELECT balance, total_ganado FROM tokens WHERE user_id=?", (user_id,))
    t = c.fetchone()
    conn.close()
    
    teclado = InlineKeyboardMarkup([[InlineKeyboardButton("Volver al menu", callback_data="volver_start")]])
    
    if not t:
        await mensaje(
            "🪙 TOKENS ESTELAR (EST)\n\n"
            "No tienes tokens todavia.\n"
            "Completa expediciones para ganar EST.\n\n"
            "Generacion por sector:\n"
            "🟢 High Sec: 10% del oro\n"
            "🟡 Low Sec: 25% del oro\n"
            "🔴 Null Sec: 50% del oro\n\n"
            "Canje por USDT (TON) cada 30 dias.",
            reply_markup=teclado
        )
        return
    
    await mensaje(
        f"🪙 TOKENS ESTELAR (EST)\n\n"
        f"Balance actual: {t[0]} EST\n"
        f"Total ganado: {t[1]} EST\n\n"
        f"Generacion por sector:\n"
        f"🟢 High Sec: 10% del oro\n"
        f"🟡 Low Sec: 25% del oro\n"
        f"🔴 Null Sec: 50% del oro\n\n"
        f"Canje por USDT (TON) cada 30 dias.\n"
        f"Usa /pool para ver el estado del fondo.",
        reply_markup=teclado
    )

async def info_pool(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect('estelar.db')
    c = conn.cursor()
    
    c.execute("SELECT SUM(balance) FROM tokens")
    total_est = c.fetchone()[0] or 0
    
    c.execute("SELECT SUM(costo) FROM naves")
    invertido = c.fetchone()[0] or 0
    
    pool = round(invertido * 0.7, 2)
    conn.close()
    
    if total_est > 0:
        tasa = round(pool / total_est, 6)
    else:
        tasa = 0
    
    await update.message.reply_text(
        f"💎 POOL DE CANJE EST/USDT\n\n"
        f"Total invertido en naves: {invertido} oro\n"
        f"Pool disponible (70%): {pool} USDT\n"
        f"EST en circulacion: {total_est}\n"
        f"Tasa estimada: 1 EST = {tasa} USDT\n\n"
        f"Proximo canje: en 30 dias\n"
        f"El pool se actualiza con cada compra de nave."
    )
# ============ TABLON ============

async def publicar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        mensaje = query.edit_message_text
    else:
        user_id = update.message.from_user.id
        mensaje = update.message.reply_text
    
    conn = sqlite3.connect('estelar.db')
    c = conn.cursor()
    c.execute("SELECT * FROM personajes WHERE user_id=?", (user_id,))
    p = c.fetchone()
    if not p:
        conn.close()
        await mensaje("Primero crea tu personaje.")
        return
    if p[6] == 0:
        conn.close()
        await mensaje("No tienes nave activa.")
        return
    
    nave_id = p[6]
    mi_oficio = p[2]
    
    c.execute("SELECT oficio FROM tripulacion WHERE nave_id=?", (nave_id,))
    ocupados = [row[0] for row in c.fetchall()]
    
    conteo = {"piloto": 0, "armero": 0, "minero": 0}
    conteo[mi_oficio] += 1
    for o in ocupados:
        if o in conteo:
            conteo[o] += 1
    
    c.execute("SELECT nombre, tipo FROM naves WHERE id=?", (nave_id,))
    nave = c.fetchone()
    conn.close()
    
    texto = f"PUBLICAR ANUNCIO\n\nNave: {nave[0]} ({nave[1]})\n\nTripulacion actual:\n"
    for oficio, cant in conteo.items():
        texto += f"  {oficio.capitalize()}: {cant}\n"
    
    teclado = []
    for oficio in ["piloto", "armero", "minero"]:
        teclado.append([InlineKeyboardButton(f"Pedir {oficio.capitalize()}", callback_data=f"pedir_{oficio}")])
    teclado.append([InlineKeyboardButton("Volver al menu", callback_data="volver_start")])
    
    await mensaje(texto, reply_markup=InlineKeyboardMarkup(teclado))

async def pedir_oficio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    oficio = query.data.replace("pedir_", "")
    context.user_data["oficio_pedido"] = oficio
    
    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("1", callback_data="cant_1"),
         InlineKeyboardButton("2", callback_data="cant_2"),
         InlineKeyboardButton("3", callback_data="cant_3")],
        [InlineKeyboardButton("Volver", callback_data="menu_publicar")]
    ])
    
    await query.edit_message_text(f"Cuantos {oficio.capitalize()} necesitas?", reply_markup=teclado)

async def confirmar_anuncio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    cantidad = int(query.data.replace("cant_", ""))
    oficio = context.user_data.get("oficio_pedido", "piloto")
    
    conn = sqlite3.connect('estelar.db')
    c = conn.cursor()
    c.execute("SELECT nave_activa, nombre FROM personajes WHERE user_id=?", (user_id,))
    p = c.fetchone()
    nave_id = p[0]
    
    c.execute("SELECT nombre, tipo FROM naves WHERE id=?", (nave_id,))
    nave = c.fetchone()
    
    c.execute("DELETE FROM tablon WHERE capitan_id=?", (user_id,))
    c.execute("INSERT INTO tablon (capitan_id, nombre_capitan, nave_nombre, nave_tipo, oficio_buscado, cantidad_total, cantidad_actual) VALUES (?, ?, ?, ?, ?, ?, 0)",
              (user_id, p[1], nave[0], nave[1], oficio, cantidad))
    conn.commit()
    conn.close()
    
    teclado = InlineKeyboardMarkup([[InlineKeyboardButton("Volver al menu", callback_data="volver_start")]])
    await query.edit_message_text(f"ANUNCIO PUBLICADO\n\n{p[1]} busca {cantidad}x {oficio.capitalize()}\nNave: {nave[0]} ({nave[1]})", reply_markup=teclado)

async def tablon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        mensaje = query.edit_message_text
    else:
        user_id = update.message.from_user.id
        mensaje = update.message.reply_text
    
    conn = sqlite3.connect('estelar.db')
    c = conn.cursor()
    c.execute("SELECT oficio FROM personajes WHERE user_id=?", (user_id,))
    p = c.fetchone()
    if not p:
        conn.close()
        await mensaje("No tienes personaje.")
        return
    
    mi_oficio = p[0]
    c.execute("SELECT * FROM tablon WHERE activo=1 AND oficio_buscado=? AND cantidad_actual < cantidad_total", (mi_oficio,))
    anuncios = c.fetchall()
    conn.close()
    
    if not anuncios:
        teclado = InlineKeyboardMarkup([[InlineKeyboardButton("Volver al menu", callback_data="volver_start")]])
        await mensaje(f"TABLON\n\nEres {mi_oficio.capitalize()}.\n\nNo hay anuncios para tu oficio.", reply_markup=teclado)
        return
    
    texto = f"TABLON - Eres {mi_oficio.capitalize()}\n\n"
    teclado = []
    for a in anuncios:
        faltan = a[6] - a[7]
        texto += f"{a[2]} - {a[4]} busca {a[5].capitalize()} ({faltan}/{a[6]})\n\n"
        teclado.append([InlineKeyboardButton(f"Unirme a {a[2]}", callback_data=f"unirme_{a[0]}")])
    teclado.append([InlineKeyboardButton("Volver al menu", callback_data="volver_start")])
    
    await mensaje(texto, reply_markup=InlineKeyboardMarkup(teclado))

async def unirme_a_nave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    anuncio_id = int(query.data.replace("unirme_", ""))
    
    conn = sqlite3.connect('estelar.db')
    c = conn.cursor()
    c.execute("SELECT * FROM tablon WHERE id=? AND activo=1", (anuncio_id,))
    anuncio = c.fetchone()
    if not anuncio:
        conn.close()
        await query.edit_message_text("Anuncio no disponible.")
        return
    
    if anuncio[7] >= anuncio[6]:
        c.execute("UPDATE tablon SET activo=0 WHERE id=?", (anuncio_id,))
        conn.commit()
        conn.close()
        await query.edit_message_text("Anuncio completo.")
        return
    
    capitan_id = anuncio[1]
    
    c.execute("SELECT oficio, nombre FROM personajes WHERE user_id=?", (user_id,))
    p = c.fetchone()
    if not p or p[0] != anuncio[5]:
        conn.close()
        await query.edit_message_text("No cumples el oficio requerido.")
        return
    
    c.execute("SELECT nave_activa FROM personajes WHERE user_id=?", (capitan_id,))
    cap = c.fetchone()
    if not cap or cap[0] == 0:
        c.execute("UPDATE tablon SET activo=0 WHERE id=?", (anuncio_id,))
        conn.commit()
        conn.close()
        await query.edit_message_text("El capitan ya no tiene nave.")
        return
    
    nave_id = cap[0]
    
    c.execute("SELECT * FROM tripulacion WHERE nave_id=? AND user_id=?", (nave_id, user_id))
    if c.fetchone():
        conn.close()
        await query.edit_message_text("Ya estas en esa tripulacion.")
        return
    
    c.execute("INSERT INTO tripulacion (nave_id, user_id, oficio) VALUES (?, ?, ?)", (nave_id, user_id, p[0]))
    c.execute("UPDATE tablon SET cantidad_actual = cantidad_actual + 1 WHERE id=?", (anuncio_id,))
    c.execute("SELECT cantidad_actual, cantidad_total FROM tablon WHERE id=?", (anuncio_id,))
    act, total = c.fetchone()
    if act >= total:
        c.execute("UPDATE tablon SET activo=0 WHERE id=?", (anuncio_id,))
    
    conn.commit()
    conn.close()
    
    try:
        await context.bot.send_message(capitan_id, f"{p[1]} ({p[0]}) se ha unido a tu nave!")
    except:
        pass
    
    teclado = InlineKeyboardMarkup([[InlineKeyboardButton("Volver al menu", callback_data="volver_start")]])
    await query.edit_message_text(f"Te has unido a la nave de {anuncio[2]} como {p[0].capitalize()}!", reply_markup=teclado)

async def cancelar_publicacion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        mensaje = query.edit_message_text
    else:
        user_id = update.message.from_user.id
        mensaje = update.message.reply_text
    
    conn = sqlite3.connect('estelar.db')
    c = conn.cursor()
    c.execute("DELETE FROM tablon WHERE capitan_id=?", (user_id,))
    conn.commit()
    conn.close()
    
    teclado = InlineKeyboardMarkup([[InlineKeyboardButton("Volver al menu", callback_data="volver_start")]])
    await mensaje("Anuncio cancelado.", reply_markup=teclado)

async def ver_tripulacion(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        mensaje = query.edit_message_text
    else:
        user_id = update.message.from_user.id
        mensaje = update.message.reply_text
    
    conn = sqlite3.connect('estelar.db')
    c = conn.cursor()
    c.execute("SELECT nave_activa, nombre, oficio FROM personajes WHERE user_id=?", (user_id,))
    p = c.fetchone()
    
    if not p or p[0] == 0:
        conn.close()
        teclado = InlineKeyboardMarkup([[InlineKeyboardButton("Volver al menu", callback_data="volver_start")]])
        await mensaje("No tienes nave activa.", reply_markup=teclado)
        return
    
    nave_id = p[0]
    c.execute("SELECT nombre, tipo FROM naves WHERE id=?", (nave_id,))
    nave = c.fetchone()
    
    c.execute("SELECT tripulacion.oficio, personajes.nombre FROM tripulacion JOIN personajes ON tripulacion.user_id = personajes.user_id WHERE nave_id=?", (nave_id,))
    trip = c.fetchall()
    conn.close()
    
    texto = f"TRIPULACION DE {nave[0]} ({nave[1]})\n\n"
    texto += f"Capitan: {p[1]} ({p[2]})\n\nTripulantes:\n"
    
    if trip:
        for t in trip:
            texto += f"  {t[1]} ({t[0]})\n"
    else:
        texto += "  Sin tripulantes.\n"
    
    teclado = InlineKeyboardMarkup([[InlineKeyboardButton("Volver al menu", callback_data="volver_start")]])
    await mensaje(texto, reply_markup=teclado)

async def volver_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    
    conn = sqlite3.connect('estelar.db')
    c = conn.cursor()
    c.execute("SELECT * FROM personajes WHERE user_id=?", (user_id,))
    p = c.fetchone()
    conn.close()
    
    if p:
        teclado = InlineKeyboardMarkup([
            [InlineKeyboardButton("Stats", callback_data="menu_stats")],
            [InlineKeyboardButton("Naves", callback_data="menu_nave")],
            [InlineKeyboardButton("Tablon", callback_data="menu_tablon")],
            [InlineKeyboardButton("Tripulacion", callback_data="menu_trip")],
            [InlineKeyboardButton("Publicar anuncio", callback_data="menu_publicar")],
            [InlineKeyboardButton("Cancelar anuncio", callback_data="menu_cancelar")],
            [InlineKeyboardButton("Ayuda", callback_data="menu_ayuda")],
            [InlineKeyboardButton("Expediciones", callback_data="menu_exp")],
            [InlineKeyboardButton("Tokens EST", callback_data="menu_tokens")],
        ])
        await query.edit_message_text(
            f"FRONTERA ESTELAR\n\nCapitan: {p[1]} ({p[2].capitalize()})\n\nElige una opcion:",
            reply_markup=teclado
        )
    else:
        teclado = InlineKeyboardMarkup([
            [InlineKeyboardButton("Crear personaje", callback_data="crear_menu")],
            [InlineKeyboardButton("Ver oficios", callback_data="oficios_info")]
        ])
        await query.edit_message_text("Bienvenido a la Frontera Estelar", reply_markup=teclado)

async def menu_ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    teclado = InlineKeyboardMarkup([[InlineKeyboardButton("Volver al menu", callback_data="volver_start")]])
    await query.edit_message_text("Usa los botones del menu para navegar.", reply_markup=teclado)

async def ayuda(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Usa /start para ver el menu principal.")

app = ApplicationBuilder().token("8038564215:AAEDqfNqIEtFUMA4gLT4CJ_NwvKV3FrvVk8").build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(CommandHandler("nave", nave_menu))
app.add_handler(CommandHandler("publicar", publicar))
app.add_handler(CommandHandler("tablon", tablon))
app.add_handler(CommandHandler("tripulacion", ver_tripulacion))
app.add_handler(CommandHandler("cancelar", cancelar_publicacion))
app.add_handler(CommandHandler("ayuda", ayuda))

app.add_handler(CallbackQueryHandler(oficios_info, pattern="oficios_info"))
app.add_handler(CallbackQueryHandler(crear_menu, pattern="crear_menu"))
app.add_handler(CallbackQueryHandler(crear_personaje, pattern="crear_piloto|crear_armero|crear_minero"))
app.add_handler(CallbackQueryHandler(ver_naves, pattern="ver_naves"))
app.add_handler(CallbackQueryHandler(comprar_nave_menu, pattern="comprar_nave"))
app.add_handler(CallbackQueryHandler(comprar_nave, pattern="comprar_"))
app.add_handler(CallbackQueryHandler(seleccionar_nave, pattern="sel_nave"))
app.add_handler(CallbackQueryHandler(activar_nave, pattern="activar_"))
app.add_handler(CallbackQueryHandler(volver_nave, pattern="volver_nave"))
app.add_handler(CallbackQueryHandler(pedir_oficio, pattern="pedir_"))
app.add_handler(CallbackQueryHandler(confirmar_anuncio, pattern="cant_"))
app.add_handler(CallbackQueryHandler(unirme_a_nave, pattern="unirme_"))
app.add_handler(CallbackQueryHandler(stats, pattern="menu_stats"))
app.add_handler(CallbackQueryHandler(nave_menu, pattern="menu_nave"))
app.add_handler(CallbackQueryHandler(tablon, pattern="menu_tablon"))
app.add_handler(CallbackQueryHandler(ver_tripulacion, pattern="menu_trip"))
app.add_handler(CallbackQueryHandler(publicar, pattern="menu_publicar"))
app.add_handler(CallbackQueryHandler(cancelar_publicacion, pattern="menu_cancelar"))
app.add_handler(CallbackQueryHandler(menu_ayuda, pattern="menu_ayuda"))
app.add_handler(CallbackQueryHandler(volver_start, pattern="volver_start"))
app.add_handler(CommandHandler("expedicion", expedicion_menu))
app.add_handler(CommandHandler("tokens", ver_tokens))
app.add_handler(CommandHandler("pool", info_pool))
app.add_handler(CallbackQueryHandler(expedicion_menu, pattern="menu_exp"))
app.add_handler(CallbackQueryHandler(elegir_expedicion, pattern="sector_"))
app.add_handler(CallbackQueryHandler(iniciar_expedicion, pattern="exp_"))
app.add_handler(CallbackQueryHandler(cancelar_expedicion, pattern="cancelar_exp"))
app.add_handler(CallbackQueryHandler(ver_tokens, pattern="menu_tokens"))
app.add_handler(CommandHandler("expedicion", expedicion_menu))
app.add_handler(CommandHandler("reparar", reparar_nave))
app.add_handler(CallbackQueryHandler(expedicion_menu, pattern="menu_exp"))
app.add_handler(CallbackQueryHandler(elegir_expedicion, pattern="sector_"))
app.add_handler(CallbackQueryHandler(iniciar_expedicion, pattern="exp_"))
app.add_handler(CallbackQueryHandler(iniciar_expedicion_rara, pattern="rara_"))
app.add_handler(CallbackQueryHandler(cancelar_expedicion, pattern="cancelar_exp"))
app.add_handler(CallbackQueryHandler(estadisticas_exp, pattern="menu_stats_exp"))
app.add_handler(CallbackQueryHandler(reparar_nave, pattern="menu_reparar"))
app.add_handler(CallbackQueryHandler(confirmar_reparar, pattern="confirmar_reparar"))
app.add_handler(CommandHandler("tokens", ver_tokens))
app.add_handler(CommandHandler("pool", info_pool))
app.add_handler(CallbackQueryHandler(ver_tokens, pattern="menu_tokens"))
app.add_handler(CommandHandler("stats_p", ver_stats_personaje))
app.add_handler(CallbackQueryHandler(ver_stats_personaje, pattern="menu_stats_p"))
app.add_handler(CallbackQueryHandler(mejorar_stat, pattern="mejorar_"))
print("Bot iniciado...")
app.run_polling()


