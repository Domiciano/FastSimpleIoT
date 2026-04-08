# Desplegar la API en una instancia EC2

Estos pasos asumen una instancia **Amazon Linux 2023** o **Ubuntu 22.04** recién creada.

---

## 1. Instalar Python y pip

**Amazon Linux 2023**
```bash
sudo dnf install -y python3 python3-pip
```

**Ubuntu**
```bash
sudo apt update
sudo apt install -y python3 python3-pip
```

Verificar:
```bash
python3 --version
pip3 --version
```

---

## 2. Instalar Git

**Amazon Linux 2023**
```bash
sudo dnf install -y git
```

**Ubuntu**
```bash
sudo apt install -y git
```

---

## 3. Clonar el repositorio

```bash
git clone https://github.com/Domiciano/FastSimpleIoT
cd FastSimpleIoT
```

---

## 4. Instalar dependencias

```bash
pip3 install -r requirements.txt
```

---

## 5. Configurar la base de datos

La app lee la URL de conexión desde una variable de entorno. Para que persista
entre sesiones, agrégala a `~/.bashrc`:

```bash
echo 'export DATABASE_URL="postgresql://usuario:password@host:5432/nombre_db"' >> ~/.bashrc
source ~/.bashrc
```

`~/.bashrc` se ejecuta automáticamente al iniciar cada sesión, por lo que la
variable estará disponible aunque cierres y vuelvas a conectarte a la instancia.

---

## 6. Ejecutar la app

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

La API queda disponible en `http://<ip-publica-ec2>:8000`

> Asegúrate de que el **Security Group** de la instancia tenga el puerto **8000** abierto para tráfico entrante.
