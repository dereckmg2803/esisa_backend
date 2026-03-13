from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
from send_email import send_contact_emails

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# ===== MODELS =====

class Product(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    slug: str
    name_es: str
    name_en: str
    description_es: str
    description_en: str
    price: float
    original_price: Optional[float] = None
    category: str
    images: List[str]
    sizes: Optional[List[str]] = None
    colors: Optional[List[str]] = None
    badge: Optional[str] = None
    featured: bool = False
    in_stock: bool = True

class Category(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    slug: str
    name_es: str
    name_en: str
    image: str
    description_es: str
    description_en: str

class ContactRequest(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    message: str
    products: Optional[List[str]] = None

class ContactResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    message: str
    products: Optional[List[str]] = None
    created_at: str

# ===== HARDCODED DATA =====

CATEGORIES: List[Category] = [
    Category(
        id="1",
        slug="ropa",
        name_es="Ropa",
        name_en="Clothing",
        image="https://images.unsplash.com/photo-1558171813-4c088753af8f?w=600",
        description_es="Prendas artesanales con diseños caribeños",
        description_en="Handcrafted clothing with Caribbean designs"
    ),
    Category(
        id="2",
        slug="accesorios",
        name_es="Accesorios",
        name_en="Accessories",
        image="https://images.unsplash.com/photo-1611085583191-a3b181a88401?w=600",
        description_es="Complementos únicos inspirados en Colombia",
        description_en="Unique accessories inspired by Colombia"
    ),
    Category(
        id="3",
        slug="bolsos",
        name_es="Bolsos",
        name_en="Bags",
        image="https://images.unsplash.com/photo-1590874103328-eac38a683ce7?w=600",
        description_es="Bolsos artesanales wayuu y mochilas",
        description_en="Handcrafted wayuu bags and backpacks"
    ),
    Category(
        id="4",
        slug="libros",
        name_es="Libros",
        name_en="Books",
        image="https://images.unsplash.com/photo-1512820790803-83ca734da794?w=600",
        description_es="Literatura colombiana y Gabriel García Márquez",
        description_en="Colombian literature and Gabriel García Márquez"
    ),
]

PRODUCTS: List[Product] = [
   # ===== NUEVOS PRODUCTOS =====

Product(
    id="1",
    slug="bolso-artesanal-bandera-colombiana",
    name_es="Bolso Artesanal Bandera Colombiana",
    name_en="Colombian Flag Handcrafted Bag",
    description_es="Bolso artesanal inspirado en los colores de la bandera colombiana. Hecho a mano con materiales resistentes.",
    description_en="Handcrafted bag inspired by the colors of the Colombian flag. Handmade with durable materials.",
    price=85.00,
    category="bolsos",
    images=["https://storage.googleapis.com/gym_bt/wb-pics/bolso-artesanal-bandera-colombiana.png"],
    colors=["Amarillo/Azul/Rojo"],
    featured=True
),

Product(
    id="2",
    slug="camisa-marimonda",
    name_es="Camisa Marimonda",
    name_en="Marimonda Shirt",
    description_es="Camisa inspirada en el personaje tradicional del Carnaval de Barranquilla: la marimonda.",
    description_en="Shirt inspired by the traditional Barranquilla Carnival character: the marimonda.",
    price=65.00,
    category="ropa",
    images=["https://storage.googleapis.com/gym_bt/wb-pics/camisa-marimonda.jpg"],
    sizes=["S","M","L","XL"],
    colors=["Multicolor"],
    featured=True
),

Product(
    id="3",
    slug="camisa-roja-toros",
    name_es="Camisa Roja Toros",
    name_en="Red Bulls Shirt",
    description_es="Camisa roja con ilustraciones de toros inspiradas en la cultura festiva del Caribe colombiano.",
    description_en="Red shirt with bull illustrations inspired by the festive culture of the Colombian Caribbean.",
    price=62.00,
    category="ropa",
    images=["https://storage.googleapis.com/gym_bt/wb-pics/camisa-roja-toros.jpg"],
    sizes=["S","M","L","XL"],
    colors=["Rojo"],
    featured=False
),

Product(
    id="4",
    slug="camisa-sombrero-vueltiao",
    name_es="Camisa Sombrero Vueltiao",
    name_en="Vueltiao Hat Shirt",
    description_es="Camisa con estampado del tradicional sombrero vueltiao, símbolo del Caribe colombiano.",
    description_en="Shirt with print of the traditional vueltiao hat, symbol of the Colombian Caribbean.",
    price=64.00,
    category="ropa",
    images=["https://storage.googleapis.com/gym_bt/wb-pics/camisa-sombrerovolteados.jpg"],
    sizes=["S","M","L","XL"],
    colors=["Blanco/Negro"],
    featured=True
),

Product(
    id="5",
    slug="camiseta-amarilla-jergas-caribenas",
    name_es="Camiseta Amarilla Jergas Caribeñas",
    name_en="Yellow Caribbean Slang T-Shirt",
    description_es="Camiseta amarilla con frases y jergas típicas del Caribe colombiano.",
    description_en="Yellow t-shirt with phrases and slang typical of the Colombian Caribbean.",
    price=38.00,
    category="ropa",
    images=["https://storage.googleapis.com/gym_bt/wb-pics/camiseta-amarilla-jergas-caribenas.jpg"],
    sizes=["S","M","L","XL"],
    colors=["Amarillo"],
    featured=False
),

Product(
    id="6",
    slug="camiseta-blanca-marimondas-flores",
    name_es="Camiseta Blanca Marimondas y Flores",
    name_en="White Marimondas and Flowers T-Shirt",
    description_es="Camiseta blanca con ilustraciones de marimondas y flores tropicales.",
    description_en="White t-shirt with marimondas and tropical flower illustrations.",
    price=40.00,
    category="ropa",
    images=["https://storage.googleapis.com/gym_bt/wb-pics/camiseta-blanca-marimondas-flores.jpg"],
    sizes=["S","M","L","XL"],
    colors=["Blanco"],
    featured=True
),

Product(
    id="7",
    slug="collar-flor-amarilla-roja",
    name_es="Collar Flor Amarilla y Roja",
    name_en="Yellow and Red Flower Necklace",
    description_es="Collar artesanal con flor en tonos amarillo y rojo inspirado en la naturaleza tropical.",
    description_en="Handcrafted necklace with yellow and red flower inspired by tropical nature.",
    price=26.00,
    category="accesorios",
    images=["https://storage.googleapis.com/gym_bt/wb-pics/collar-flor-amarilla-roja.png"],
    colors=["Amarillo/Rojo"],
    featured=False
),

Product(
    id="8",
    slug="libro-hasta-agosto",
    name_es="En Agosto Nos Vemos",
    name_en="Until August",
    description_es="Obra póstuma de Gabriel García Márquez publicada recientemente.",
    description_en="Posthumous work by Gabriel García Márquez recently published.",
    price=42.00,
    category="libros",
    images=["https://storage.googleapis.com/gym_bt/wb-pics/libro-gabriel-garcia-marquez-hasta-agosto.png"],
    featured=True
),

Product(
    id="9",
    slug="manilla-bandera-colombia",
    name_es="Manilla Bandera Colombia",
    name_en="Colombia Flag Bracelet",
    description_es="Manilla artesanal con los colores de la bandera colombiana.",
    description_en="Handcrafted bracelet with the colors of the Colombian flag.",
    price=15.00,
    category="accesorios",
    images=["https://storage.googleapis.com/gym_bt/wb-pics/manilla-bandera-colombia.png"],
    colors=["Amarillo/Azul/Rojo"],
    featured=False
),

Product(
    id="10",
    slug="top-mujer-flores",
    name_es="Top Mujer Flores Tropicales",
    name_en="Tropical Flower Women's Top",
    description_es="Top femenino con estampado de flores tropicales inspirado en el Caribe colombiano.",
    description_en="Women's top with tropical flower print inspired by the Colombian Caribbean.",
    price=48.00,
    category="ropa",
    images=["https://storage.googleapis.com/gym_bt/wb-pics/top-mujer-flores.jpg"],
    sizes=["XS","S","M","L"],
    colors=["Multicolor"],
    featured=True
),

Product(
    id="11",
    slug="turbante-blanco-verde",
    name_es="Turbante Blanco y Verde",
    name_en="White and Green Turban",
    description_es="Elegante turbante en tonos blanco y verde, tejido a mano con algodón de alta calidad.",
    description_en="Elegant turban in white and green tones, hand-woven with high-quality cotton.",
    price=29.99,
    category="accesorios",
    images=["https://storage.googleapis.com/gym_bt/wb-pics/turbante-blanco-verde.png"],
    colors=["Blanco/Verde"],
    featured=True
),

Product(
    id="12",
    slug="vestido-guacamaya-flores",
    name_es="Vestido Guacamaya y Flores",
    name_en="Macaw and Flowers Dress",
    description_es="Vestido vibrante con ilustraciones de guacamayas y flores tropicales.",
    description_en="Vibrant dress with macaws and tropical flowers illustrations.",
    price=250.00,
    category="ropa",
    images=["https://storage.googleapis.com/gym_bt/wb-pics/vestido-guacamaya-flores.png"],
    sizes=["XS","S","M","L"],
    colors=["Multicolor"],
    featured=True
),
]

# ===== ROUTES =====

@api_router.get("/")
async def root():
    return {"message": "Bienvenido a Glenia y Macondo API"}

@api_router.get("/categories", response_model=List[Category])
async def get_categories():
    return CATEGORIES

@api_router.get("/categories/{slug}", response_model=Category)
async def get_category(slug: str):
    for cat in CATEGORIES:
        if cat.slug == slug:
            return cat
    raise HTTPException(status_code=404, detail="Category not found")

@api_router.get("/products", response_model=List[Product])
async def get_products(category: Optional[str] = None, featured: Optional[bool] = None):
    result = PRODUCTS
    if category:
        result = [p for p in result if p.category == category]
    if featured is not None:
        result = [p for p in result if p.featured == featured]
    return result

@api_router.get("/products/{slug}", response_model=Product)
async def get_product(slug: str):
    for product in PRODUCTS:
        if product.slug == slug:
            return product
    raise HTTPException(status_code=404, detail="Product not found")

@api_router.post("/contact", response_model=ContactResponse, status_code=201)
async def create_contact(contact: ContactRequest):

    contact_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()

    contact_doc = {
        "id": contact_id,
        "name": contact.name,
        "email": contact.email,
        "phone": contact.phone,
        "message": contact.message,
        "products": contact.products,
        "created_at": created_at
    }

    await db.contacts.insert_one(contact_doc)

    # enviar emails
    await send_contact_emails(contact)

    return ContactResponse(**{k: v for k, v in contact_doc.items() if k != "_id"})

@api_router.get("/featured-products", response_model=List[Product])
async def get_featured_products():
    return [p for p in PRODUCTS if p.featured]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
