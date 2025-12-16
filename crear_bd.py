import mysql.connector

try:
    conexion = mysql.connector.connect(host='localhost', user='root', password='')
    cursor = conexion.cursor()

    cursor.execute("DROP DATABASE IF EXISTS turnos_saas")
    cursor.execute("CREATE DATABASE turnos_saas CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
    cursor.execute("USE turnos_saas")

    # Tabla USUARIOS
    cursor.execute("""
    CREATE TABLE usuarios (
        id INT AUTO_INCREMENT PRIMARY KEY,
        email VARCHAR(100) UNIQUE NOT NULL,
        password VARCHAR(100) NOT NULL,
        nombre_negocio VARCHAR(100) NOT NULL
    )
    """)

    # Tabla CLIENTES
    cursor.execute("""
    CREATE TABLE clientes (
        id INT AUTO_INCREMENT PRIMARY KEY,
        usuario_id INT NOT NULL,
        nombre VARCHAR(100),
        telefono VARCHAR(20),
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
    )
    """)

    # --- NUEVO: Tabla TURNOS ---
    cursor.execute("""
    CREATE TABLE turnos (
        id INT AUTO_INCREMENT PRIMARY KEY,
        usuario_id INT NOT NULL,
        cliente_id INT NOT NULL,
        fecha DATETIME NOT NULL,
        detalle VARCHAR(200),
        estado ENUM('pendiente', 'finalizado', 'cancelado') DEFAULT 'pendiente',
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
        FOREIGN KEY (cliente_id) REFERENCES clientes(id)
    )
    """)

    # Datos de prueba
    cursor.execute("""
    INSERT INTO usuarios (email, password, nombre_negocio) VALUES 
    ('juan@peluqueria.com', '1234', 'Peluquería Juan'),
    ('ana@taller.com', '1234', 'Taller Ana')
    """)
    conexion.commit()
    print("✅ Base de Datos Actualizada con Tabla de Turnos.")

    cursor.close()
    conexion.close()

except Exception as e:
    print(f"❌ Error: {e}")