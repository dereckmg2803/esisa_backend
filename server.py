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
    # ROPA
    Product(
        id="1",
        slug="camisa-fiesta-caribena",
        name_es="Camisa Fiesta Caribeña",
        name_en="Caribbean Party Shirt",
        description_es="Camisa colorida inspirada en el Caribe colombiano, con mariposas, sombrero vueltiao, marimondas y símbolos típicos. Perfecta para celebrar nuestra cultura.",
        description_en="Colorful shirt inspired by the Colombian Caribbean, with butterflies, vueltiao hat, marimondas and typical symbols. Perfect to celebrate our culture.",
        price=65.00,
        original_price=80.00,
        category="ropa",
        images=["https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=600"],
        sizes=["S", "M", "L", "XL"],
        colors=["Multicolor"],
        badge="Nuevo",
        featured=True
    ),
    Product(
        id="2",
        slug="blusa-mariposa-tropical",
        name_es="Blusa Mariposa Tropical",
        name_en="Tropical Butterfly Blouse",
        description_es="Blusa con estampado de mariposas y flores tropicales. Diseño exclusivo que captura la esencia del Caribe.",
        description_en="Blouse with butterfly and tropical flower print. Exclusive design that captures the essence of the Caribbean.",
        price=55.00,
        original_price=70.00,
        category="ropa",
        images=["https://images.unsplash.com/photo-1564257631407-4deb1f99d992?w=600"],
        sizes=["XS", "S", "M", "L"],
        colors=["Rosa", "Amarillo"],
        badge="Oferta",
        featured=True
    ),
    Product(
        id="3",
        slug="camiseta-eche-costeño",
        name_es="Camiseta 'Eche' Costeño",
        name_en="'Eche' Coastal T-Shirt",
        description_es="Camiseta con la expresión costeña 'Eche'. Algodón 100% con diseño artístico que celebra el lenguaje caribeño.",
        description_en="T-shirt with the coastal expression 'Eche'. 100% cotton with artistic design celebrating Caribbean language.",
        price=35.00,
        category="ropa",
        images=["https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=600"],
        sizes=["S", "M", "L", "XL", "XXL"],
        colors=["Blanco", "Negro", "Amarillo"],
        featured=False
    ),
    Product(
        id="4",
        slug="vestido-carnaval-barranquilla",
        name_es="Vestido Carnaval de Barranquilla",
        name_en="Barranquilla Carnival Dress",
        description_es="Vestido vibrante inspirado en el Carnaval de Barranquilla con estampados de marimondas y colores festivos.",
        description_en="Vibrant dress inspired by Barranquilla Carnival with marimonda prints and festive colors.",
        price=95.00,
        original_price=120.00,
        category="ropa",
        images=["https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=600"],
        sizes=["XS", "S", "M", "L"],
        colors=["Multicolor"],
        badge="Destacado",
        featured=True
    ),
    # ACCESORIOS
    Product(
        id="5",
        slug="turbante-colombiano",
        name_es="Turbante Colombiano",
        name_en="Colombian Turban",
        description_es="Turbante tradicional con patrones coloridos. Símbolo de orgullo y herencia afrocaribeña.",
        description_en="Traditional turban with colorful patterns. Symbol of pride and Afro-Caribbean heritage.",
        price=45.00,
        original_price=60.00,
        category="accesorios",
        images=["https://images.unsplash.com/photo-1589810635657-232948472d98?w=600"],
        colors=["Multicolor", "Rojo/Amarillo", "Verde/Dorado"],
        badge="Popular",
        featured=True
    ),
    Product(
        id="6",
        slug="aretes-guacamaya",
        name_es="Aretes Guacamaya",
        name_en="Macaw Earrings",
        description_es="Aretes artesanales con forma de guacamaya. Hechos a mano con materiales naturales.",
        description_en="Handcrafted macaw-shaped earrings. Handmade with natural materials.",
        price=28.00,
        category="accesorios",
        images=["https://images.unsplash.com/photo-1630019852942-f89202989a59?w=600"],
        colors=["Rojo/Azul", "Verde/Amarillo"],
        featured=False
    ),
    Product(
        id="7",
        slug="collar-bandera-colombia",
        name_es="Collar Bandera Colombia",
        name_en="Colombia Flag Necklace",
        description_es="Collar con los colores de la bandera colombiana. Orgullo patrio en cada detalle.",
        description_en="Necklace with Colombian flag colors. National pride in every detail.",
        price=32.00,
        category="accesorios",
        images=["https://images.unsplash.com/photo-1611085583191-a3b181a88401?w=600"],
        colors=["Amarillo/Azul/Rojo"],
        featured=False
    ),
    # BOLSOS
    Product(
        id="8",
        slug="bolso-artesanal-wayuu",
        name_es="Bolso Artesanal Wayuu",
        name_en="Wayuu Handcrafted Bag",
        description_es="Mochila wayuu tejida a mano por artesanas de La Guajira. Cada pieza es única con patrones tradicionales.",
        description_en="Wayuu backpack hand-woven by artisans from La Guajira. Each piece is unique with traditional patterns.",
        price=120.00,
        original_price=150.00,
        category="bolsos",
        images=["https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=600"],
        colors=["Multicolor"],
        badge="Artesanal",
        featured=True
    ),
    Product(
        id="9",
        slug="bolso-bandera-tricolor",
        name_es="Bolso Bandera Tricolor",
        name_en="Tricolor Flag Bag",
        description_es="Bolso con diseño de la bandera de Colombia. Perfecto para llevar tu orgullo patrio a todas partes.",
        description_en="Bag with Colombian flag design. Perfect to carry your national pride everywhere.",
        price=75.00,
        original_price=95.00,
        category="bolsos",
        images=["https://images.unsplash.com/photo-1566150905458-1bf1fc113f0d?w=600"],
        colors=["Amarillo/Azul/Rojo"],
        badge="Nuevo",
        featured=True
    ),
    Product(
        id="10",
        slug="morral-caribe",
        name_es="Morral del Caribe",
        name_en="Caribbean Backpack",
        description_es="Morral con estampados de flores tropicales y elementos del Caribe colombiano.",
        description_en="Backpack with tropical flower prints and Colombian Caribbean elements.",
        price=85.00,
        category="bolsos",
        images=["https://images.unsplash.com/photo-1622560480605-d83c853bc5c3?w=600"],
        colors=["Multicolor"],
        featured=False
    ),
    # LIBROS
    Product(
        id="11",
        slug="cien-anos-de-soledad",
        name_es="Cien Años de Soledad",
        name_en="One Hundred Years of Solitude",
        description_es="La obra maestra de Gabriel García Márquez. Edición especial con ilustraciones inspiradas en Macondo.",
        description_en="Gabriel García Márquez's masterpiece. Special edition with illustrations inspired by Macondo.",
        price=38.00,
        original_price=45.00,
        category="libros",
        images=["https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=600"],
        badge="Clásico",
        featured=True
    ),
    Product(
        id="12",
        slug="el-amor-en-tiempos-del-colera",
        name_es="El Amor en los Tiempos del Cólera",
        name_en="Love in the Time of Cholera",
        description_es="Una historia de amor que trasciende el tiempo, ambientada en el Caribe colombiano.",
        description_en="A love story that transcends time, set in the Colombian Caribbean.",
        price=35.00,
        category="libros",
        images=["https://images.unsplash.com/photo-1543002588-bfa74002ed7e?w=600"],
        featured=True
    ),
    Product(
        id="13",
        slug="cronicas-de-una-muerte-anunciada",
        name_es="Crónica de una Muerte Anunciada",
        name_en="Chronicle of a Death Foretold",
        description_es="Novela corta que mezcla periodismo y ficción. Una joya de la literatura latinoamericana.",
        description_en="Short novel that mixes journalism and fiction. A gem of Latin American literature.",
        price=28.00,
        category="libros",
        images=["https://images.unsplash.com/photo-1512820790803-83ca734da794?w=600"],
        featured=False
    ),
    Product(
        id="14",
        slug="el-coronel-no-tiene-quien-le-escriba",
        name_es="El Coronel No Tiene Quien Le Escriba",
        name_en="No One Writes to the Colonel",
        description_es="Una de las novelas más conmovedoras de García Márquez sobre la espera y la dignidad.",
        description_en="One of García Márquez's most moving novels about waiting and dignity.",
        price=25.00,
        category="libros",
        images=["https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=600"],
        featured=False
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
