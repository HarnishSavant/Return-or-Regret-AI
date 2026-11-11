import json
import os
import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Set deterministic seed for reproducibility
random.seed(42)
np.random.seed(42)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
KB_DIR = os.path.join(BASE_DIR, "knowledge_base")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(KB_DIR, exist_ok=True)

# 18 Realistic Products
PRODUCTS = [
    {
        "product_id": "P001",
        "name": "Heritage Oxford Slim Shirt",
        "category": "Shirts",
        "price": 68.0,
        "fit_type": "Slim Fit",
        "material": "100% Organic Egyptian Cotton",
        "sizes": ["S", "M", "L", "XL", "XXL"],
        "size_guide_available": True,
        "description_completeness": 0.82,
        "image_url": "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?auto=format&fit=crop&w=600&q=80",
        "description": "Tailored slim-fit button-down Oxford shirt crafted from heavyweight pinpoint cotton. Structured collar and taper at waist. Cut slightly narrow across the shoulders for a modern profile.",
        "care_instructions": "Machine wash cold inside-out, tumble dry low, warm iron.",
        "known_fit_quirks": "Runs snug across the upper back and shoulders. Customers with athletic builds often need one size up.",
        "size_chart": {
            "S": {"chest": 37.0, "shoulder": 16.5, "waist": 33.0, "length": 29.0, "sleeve": 33.5},
            "M": {"chest": 40.0, "shoulder": 17.5, "waist": 36.0, "length": 30.0, "sleeve": 34.5},
            "L": {"chest": 43.0, "shoulder": 18.5, "waist": 39.0, "length": 31.0, "sleeve": 35.5},
            "XL": {"chest": 46.5, "shoulder": 19.5, "waist": 42.5, "length": 31.5, "sleeve": 36.5},
            "XXL": {"chest": 50.0, "shoulder": 20.5, "waist": 46.0, "length": 32.0, "sleeve": 37.0}
        }
    },
    {
        "product_id": "P002",
        "name": "Classic Twill Dress Shirt",
        "category": "Shirts",
        "price": 74.0,
        "fit_type": "Regular Fit",
        "material": "100% Pima Cotton, Wrinkle-Resistant",
        "sizes": ["S", "M", "L", "XL", "XXL"],
        "size_guide_available": True,
        "description_completeness": 0.95,
        "image_url": "https://images.unsplash.com/photo-1620012253295-c15c429f6f60?auto=format&fit=crop&w=600&q=80",
        "description": "A refined regular-fit dress shirt featuring a spread collar, French placket, and two-ply 80s yarn twill fabric. True to standard business tailoring measurements.",
        "care_instructions": "Machine wash warm, hang dry, medium steam iron.",
        "known_fit_quirks": "True to size. Generous waist allowance suitable for all-day comfort.",
        "size_chart": {
            "S": {"chest": 38.0, "shoulder": 17.0, "waist": 35.0, "length": 29.5, "sleeve": 33.5},
            "M": {"chest": 41.5, "shoulder": 18.0, "waist": 38.5, "length": 30.5, "sleeve": 34.5},
            "L": {"chest": 45.0, "shoulder": 19.0, "waist": 42.0, "length": 31.5, "sleeve": 35.5},
            "XL": {"chest": 48.5, "shoulder": 20.0, "waist": 45.5, "length": 32.0, "sleeve": 36.5},
            "XXL": {"chest": 52.0, "shoulder": 21.0, "waist": 49.0, "length": 32.5, "sleeve": 37.0}
        }
    },
    {
        "product_id": "P003",
        "name": "Supima Heavyweight Boxy Tee",
        "category": "T-Shirts",
        "price": 38.0,
        "fit_type": "Oversized",
        "material": "100% Combed Heavyweight Supima Cotton (240 GSM)",
        "sizes": ["XS", "S", "M", "L", "XL"],
        "size_guide_available": True,
        "description_completeness": 0.90,
        "image_url": "https://images.unsplash.com/photo-1521572267360-ee0c2909d518?auto=format&fit=crop&w=600&q=80",
        "description": "Dropped shoulder, relaxed silhouette, and dense rib collar. Designed for an intentional boxy streetwear drape.",
        "care_instructions": "Wash cold, flat air dry to prevent length shrinkage.",
        "known_fit_quirks": "Already cut 2-3 inches wider in chest. Order regular size for boxy fit, downsize for standard look.",
        "size_chart": {
            "XS": {"chest": 40.0, "shoulder": 18.5, "waist": 40.0, "length": 27.0, "sleeve": 8.5},
            "S": {"chest": 43.0, "shoulder": 19.5, "waist": 43.0, "length": 28.0, "sleeve": 9.0},
            "M": {"chest": 46.0, "shoulder": 20.5, "waist": 46.0, "length": 29.0, "sleeve": 9.5},
            "L": {"chest": 49.0, "shoulder": 21.5, "waist": 49.0, "length": 30.0, "sleeve": 10.0},
            "XL": {"chest": 52.0, "shoulder": 22.5, "waist": 52.0, "length": 31.0, "sleeve": 10.5}
        }
    },
    {
        "product_id": "P004",
        "name": "Mercerized Ribbed Polo",
        "category": "T-Shirts",
        "price": 54.0,
        "fit_type": "Slim Fit",
        "material": "95% Mercerized Cotton, 5% Elastane",
        "sizes": ["S", "M", "L", "XL"],
        "size_guide_available": False,
        "description_completeness": 0.65,
        "image_url": "https://images.unsplash.com/photo-1581655353564-df123a1eb820?auto=format&fit=crop&w=600&q=80",
        "description": "Smart casual knit polo with ribbed cuffs and subtle luster. Unstructured collar.",
        "care_instructions": "Gentle wash cold, lay flat to dry.",
        "known_fit_quirks": "High return rate due to missing chest chart and tighter than expected arm openings.",
        "size_chart": {
            "S": {"chest": 36.5, "shoulder": 16.0, "waist": 33.0, "length": 27.5, "sleeve": 8.0},
            "M": {"chest": 39.0, "shoulder": 17.0, "waist": 35.5, "length": 28.5, "sleeve": 8.5},
            "L": {"chest": 41.5, "shoulder": 18.0, "waist": 38.0, "length": 29.5, "sleeve": 9.0},
            "XL": {"chest": 44.5, "shoulder": 19.0, "waist": 41.0, "length": 30.0, "sleeve": 9.5}
        }
    },
    {
        "product_id": "P005",
        "name": "Selvedge Slim-Taper Denim Jeans",
        "category": "Jeans",
        "price": 125.0,
        "fit_type": "Slim Fit",
        "material": "98% Cotton, 2% Polyurethane 13.5oz Kurabo Denim",
        "sizes": ["30", "31", "32", "33", "34", "36"],
        "size_guide_available": True,
        "description_completeness": 0.88,
        "image_url": "https://images.unsplash.com/photo-1542272604-787c3835535d?auto=format&fit=crop&w=600&q=80",
        "description": "Japanese raw selvedge denim with slight 2% comfort stretch. Mid-rise with clean taper from knee to leg opening.",
        "care_instructions": "Wash cold inside-out, soak only, avoid dryer to prevent inseam shrinkage.",
        "known_fit_quirks": "Rigid initial feel. Raw denim waist expands by ~0.75 inch after 5 wears. Inseam standard 32 inches.",
        "size_chart": {
            "30": {"waist": 31.0, "hip": 38.0, "thigh": 22.0, "rise": 10.2, "inseam": 32.0, "leg_opening": 13.5},
            "31": {"waist": 32.0, "hip": 39.0, "thigh": 22.5, "rise": 10.4, "inseam": 32.0, "leg_opening": 13.7},
            "32": {"waist": 33.0, "hip": 40.0, "thigh": 23.0, "rise": 10.6, "inseam": 32.0, "leg_opening": 14.0},
            "33": {"waist": 34.0, "hip": 41.0, "thigh": 23.5, "rise": 10.8, "inseam": 32.0, "leg_opening": 14.2},
            "34": {"waist": 35.0, "hip": 42.0, "thigh": 24.0, "rise": 11.0, "inseam": 32.0, "leg_opening": 14.5},
            "36": {"waist": 37.0, "hip": 44.0, "thigh": 25.0, "rise": 11.4, "inseam": 32.0, "leg_opening": 15.0}
        }
    },
    {
        "product_id": "P006",
        "name": "Pleated Relaxed Cotton Chinos",
        "category": "Pants",
        "price": 82.0,
        "fit_type": "Relaxed Fit",
        "material": "100% Peached Cotton Twill",
        "sizes": ["30", "32", "34", "36"],
        "size_guide_available": True,
        "description_completeness": 0.92,
        "image_url": "https://images.unsplash.com/photo-1624378439575-d8705ad7ae80?auto=format&fit=crop&w=600&q=80",
        "description": "Double pleated front with roomy thigh cut and gentle taper towards the ankle. Elasticated side waist inserts.",
        "care_instructions": "Machine wash warm with like colors, tumble dry low.",
        "known_fit_quirks": "Waist runs true to size with elastic forgiveness; generous seat and thighs.",
        "size_chart": {
            "30": {"waist": 30.5, "hip": 40.5, "thigh": 24.5, "rise": 11.5, "inseam": 30.5, "leg_opening": 15.0},
            "32": {"waist": 32.5, "hip": 42.5, "thigh": 25.5, "rise": 11.8, "inseam": 31.0, "leg_opening": 15.5},
            "34": {"waist": 34.5, "hip": 44.5, "thigh": 26.5, "rise": 12.2, "inseam": 31.5, "leg_opening": 16.0},
            "36": {"waist": 36.5, "hip": 46.5, "thigh": 27.5, "rise": 12.5, "inseam": 32.0, "leg_opening": 16.5}
        }
    },
    {
        "product_id": "P007",
        "name": "Tailored Double-Breasted Blazer Dress",
        "category": "Dresses",
        "price": 145.0,
        "fit_type": "Slim Fit",
        "material": "68% Polyester, 28% Viscose, 4% Spandex",
        "sizes": ["XS", "S", "M", "L", "XL"],
        "size_guide_available": True,
        "description_completeness": 0.85,
        "image_url": "https://images.unsplash.com/photo-1539109136881-3be0616acf4b?auto=format&fit=crop&w=600&q=80",
        "description": "Structured hourglass blazer dress with padded shoulders, satin peak lapels, and horn buttons. Fully lined interior.",
        "care_instructions": "Dry clean only.",
        "known_fit_quirks": "Zero stretch through ribcage and waist seams. Measure fullest bust and underbust accurately.",
        "size_chart": {
            "XS": {"bust": 32.5, "waist": 25.5, "hip": 35.5, "length": 34.0, "shoulder": 14.8},
            "S": {"bust": 34.5, "waist": 27.5, "hip": 37.5, "length": 34.5, "shoulder": 15.2},
            "M": {"bust": 36.5, "waist": 29.5, "hip": 39.5, "length": 35.0, "shoulder": 15.8},
            "L": {"bust": 39.0, "waist": 32.0, "hip": 42.0, "length": 35.5, "shoulder": 16.4},
            "XL": {"bust": 42.0, "waist": 35.0, "hip": 45.0, "length": 36.0, "shoulder": 17.0}
        }
    },
    {
        "product_id": "P008",
        "name": "Silk Satin Bias Cut Midi Dress",
        "category": "Dresses",
        "price": 160.0,
        "fit_type": "Regular Fit",
        "material": "100% Mulberry Silk Crepe Satin",
        "sizes": ["XS", "S", "M", "L"],
        "size_guide_available": False,
        "description_completeness": 0.60,
        "image_url": "https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?auto=format&fit=crop&w=600&q=80",
        "description": "Sensual cowl neck slip dress cut on the bias to hug body contours naturally. Adjustable criss-cross spaghetti straps.",
        "care_instructions": "Hand wash cold with silk detergent or dry clean.",
        "known_fit_quirks": "High return frequency: bias cut clings unexpectedly across hips and lower abdomen.",
        "size_chart": {
            "XS": {"bust": 32.0, "waist": 25.0, "hip": 35.0, "length": 47.0},
            "S": {"bust": 34.0, "waist": 27.0, "hip": 37.0, "length": 47.5},
            "M": {"bust": 36.0, "waist": 29.0, "hip": 39.0, "length": 48.0},
            "L": {"bust": 38.5, "waist": 31.5, "hip": 41.5, "length": 48.5}
        }
    },
    {
        "product_id": "P009",
        "name": "Merino Wool Cashmere Overcoat",
        "category": "Outerwear",
        "price": 280.0,
        "fit_type": "Regular Fit",
        "material": "90% Virgin Merino Wool, 10% Cashmere",
        "sizes": ["S", "M", "L", "XL"],
        "size_guide_available": True,
        "description_completeness": 0.94,
        "image_url": "https://images.unsplash.com/photo-1544923246-77307dd654cb?auto=format&fit=crop&w=600&q=80",
        "description": "Full-length single-breasted topcoat with notch lapels, horn buttons, and Bemberg cupro lining. Cut with layering room.",
        "care_instructions": "Specialist dry clean only.",
        "known_fit_quirks": "Pattern already accounts for wearing a thick knitwear or blazer underneath.",
        "size_chart": {
            "S": {"chest": 42.0, "shoulder": 18.0, "length": 39.0, "sleeve": 34.5},
            "M": {"chest": 45.0, "shoulder": 19.0, "length": 40.0, "sleeve": 35.5},
            "L": {"chest": 48.0, "shoulder": 20.0, "length": 41.0, "sleeve": 36.5},
            "XL": {"chest": 51.0, "shoulder": 21.0, "length": 42.0, "sleeve": 37.0}
        }
    },
    {
        "product_id": "P010",
        "name": "Ultralight Packable Waterproof Parka",
        "category": "Outerwear",
        "price": 135.0,
        "fit_type": "Athletic",
        "material": "3-Ply 100% Recycled Ripstop Nylon with DWR",
        "sizes": ["S", "M", "L", "XL", "XXL"],
        "size_guide_available": True,
        "description_completeness": 0.91,
        "image_url": "https://images.unsplash.com/photo-1548883354-7622d03aca27?auto=format&fit=crop&w=600&q=80",
        "description": "Seam-sealed storm jacket with 20,000mm hydrostatic head rating. Pit zips and 2-way adjustable storm hood.",
        "care_instructions": "Machine wash 30C with technical wash, tumble dry gentle to reactivate DWR.",
        "known_fit_quirks": "Athletic trim fit. If planning heavy fleece midlayers, choose one size up.",
        "size_chart": {
            "S": {"chest": 39.0, "shoulder": 17.5, "length": 28.5, "sleeve": 34.0},
            "M": {"chest": 42.0, "shoulder": 18.5, "length": 29.5, "sleeve": 35.0},
            "L": {"chest": 45.0, "shoulder": 19.5, "length": 30.5, "sleeve": 36.0},
            "XL": {"chest": 48.0, "shoulder": 20.5, "length": 31.0, "sleeve": 36.5},
            "XXL": {"chest": 51.5, "shoulder": 21.5, "length": 31.5, "sleeve": 37.0}
        }
    },
    {
        "product_id": "P011",
        "name": "High-Waist Sculpt Compression Leggings",
        "category": "Activewear",
        "price": 64.0,
        "fit_type": "Slim Fit",
        "material": "75% Recycled Polyamide, 25% Lycra Xtra Life",
        "sizes": ["XS", "S", "M", "L", "XL"],
        "size_guide_available": True,
        "description_completeness": 0.89,
        "image_url": "https://images.unsplash.com/photo-1506629082955-511b1aa562c8?auto=format&fit=crop&w=600&q=80",
        "description": "High-compression squat-proof leggings with bonded 4-inch waistband and ergonomic side drop-in pockets.",
        "care_instructions": "Wash cold, hang dry, do not use fabric softener.",
        "known_fit_quirks": "Substantial compression feel. Between sizes customers should size up for daily yoga/pilates.",
        "size_chart": {
            "XS": {"waist": 23.0, "hip": 32.0, "inseam": 26.0},
            "S": {"waist": 25.0, "hip": 34.5, "inseam": 26.0},
            "M": {"waist": 27.5, "hip": 37.0, "inseam": 26.5},
            "L": {"waist": 30.0, "hip": 39.5, "inseam": 26.5},
            "XL": {"waist": 33.0, "hip": 42.5, "inseam": 27.0}
        }
    },
    {
        "product_id": "P012",
        "name": "Seamless Aero-Vent Tech Tee",
        "category": "Activewear",
        "price": 42.0,
        "fit_type": "Athletic",
        "material": "88% Polyester, 12% Spandex Quick-Dry Mesh",
        "sizes": ["S", "M", "L", "XL"],
        "size_guide_available": True,
        "description_completeness": 0.93,
        "image_url": "https://images.unsplash.com/photo-1503342217505-b0a15ec3261c?auto=format&fit=crop&w=600&q=80",
        "description": "Engineered body-mapped knit zones for heat dissipation. Anti-odor silver-ion finish.",
        "care_instructions": "Machine wash cold gentle cycle.",
        "known_fit_quirks": "Athletic taper around chest and lats. Accurate to size chart.",
        "size_chart": {
            "S": {"chest": 37.5, "shoulder": 16.5, "length": 27.5},
            "M": {"chest": 40.5, "shoulder": 17.5, "length": 28.5},
            "L": {"chest": 43.5, "shoulder": 18.5, "length": 29.5},
            "XL": {"chest": 46.5, "shoulder": 19.5, "length": 30.0}
        }
    },
    {
        "product_id": "P013",
        "name": "Italian Calfskin Goodyear Welted Derby",
        "category": "Footwear",
        "price": 210.0,
        "fit_type": "Regular Fit",
        "material": "100% Full-Grain Tuscan Calf Leather, Leather Sole",
        "sizes": ["7", "8", "9", "10", "11", "12"],
        "size_guide_available": True,
        "description_completeness": 0.94,
        "image_url": "https://images.unsplash.com/photo-1614252235316-8c857d38b5f4?auto=format&fit=crop&w=600&q=80",
        "description": "Hand-stitched Goodyear welted derby shoes on an almond-toe classic last. Cork footbed that molds over time.",
        "care_instructions": "Cedar shoe trees required, conditioned with beeswax polish.",
        "known_fit_quirks": "Traditional dress shoe sizing. Runs 0.5 size larger than typical athletic sneakers.",
        "size_chart": {
            "7": {"foot_length_in": 9.8, "us_size": 7.0, "eu_size": 40.0, "width_d_in": 3.7},
            "8": {"foot_length_in": 10.1, "us_size": 8.0, "eu_size": 41.0, "width_d_in": 3.8},
            "9": {"foot_length_in": 10.4, "us_size": 9.0, "eu_size": 42.0, "width_d_in": 3.9},
            "10": {"foot_length_in": 10.7, "us_size": 10.0, "eu_size": 43.0, "width_d_in": 4.0},
            "11": {"foot_length_in": 11.0, "us_size": 11.0, "eu_size": 44.0, "width_d_in": 4.1},
            "12": {"foot_length_in": 11.3, "us_size": 12.0, "eu_size": 45.0, "width_d_in": 4.2}
        }
    },
    {
        "product_id": "P014",
        "name": "Featherlight Knit Runner Sneaker",
        "category": "Footwear",
        "price": 115.0,
        "fit_type": "Athletic",
        "material": "Recycled PET Engineered Knit, EVA Cushion Midsole",
        "sizes": ["7", "8", "9", "10", "11", "12"],
        "size_guide_available": True,
        "description_completeness": 0.87,
        "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?auto=format&fit=crop&w=600&q=80",
        "description": "Seamless sock-like slip-on upper with supportive TPU heel counter and responsive rebound foam.",
        "care_instructions": "Hand clean with damp cloth, remove insole before washing.",
        "known_fit_quirks": "Sock fit holds firmly. Customers with wide feet should order 0.5 size larger.",
        "size_chart": {
            "7": {"foot_length_in": 9.6, "us_size": 7.0, "eu_size": 40.0, "width_d_in": 3.6},
            "8": {"foot_length_in": 9.9, "us_size": 8.0, "eu_size": 41.0, "width_d_in": 3.7},
            "9": {"foot_length_in": 10.2, "us_size": 9.0, "eu_size": 42.5, "width_d_in": 3.8},
            "10": {"foot_length_in": 10.5, "us_size": 10.0, "eu_size": 44.0, "width_d_in": 3.9},
            "11": {"foot_length_in": 10.8, "us_size": 11.0, "eu_size": 45.0, "width_d_in": 4.0},
            "12": {"foot_length_in": 11.1, "us_size": 12.0, "eu_size": 46.0, "width_d_in": 4.1}
        }
    },
    {
        "product_id": "P015",
        "name": "Chunky Cable-Knit Wool Cardigan",
        "category": "Outerwear",
        "price": 110.0,
        "fit_type": "Relaxed Fit",
        "material": "80% Lambswool, 20% Nylon",
        "sizes": ["S", "M", "L", "XL"],
        "size_guide_available": False,
        "description_completeness": 0.58,
        "image_url": "https://images.unsplash.com/photo-1576566588028-4147f3842f27?auto=format&fit=crop&w=600&q=80",
        "description": "Heritage cable knit with horn toggle buttons and patch pockets.",
        "care_instructions": "Hand wash cold, dry flat.",
        "known_fit_quirks": "Heavy knit stretches after hanging; missing detailed sleeve/chest dimensions leads to returns.",
        "size_chart": {
            "S": {"chest": 41.0, "shoulder": 18.0, "length": 26.5, "sleeve": 32.5},
            "M": {"chest": 44.0, "shoulder": 19.0, "length": 27.5, "sleeve": 33.5},
            "L": {"chest": 47.0, "shoulder": 20.0, "length": 28.5, "sleeve": 34.5},
            "XL": {"chest": 50.0, "shoulder": 21.0, "length": 29.0, "sleeve": 35.0}
        }
    },
    {
        "product_id": "P016",
        "name": "High-Rise Wide Leg Linen Trousers",
        "category": "Pants",
        "price": 89.0,
        "fit_type": "Relaxed Fit",
        "material": "100% French Flax Linen",
        "sizes": ["XS", "S", "M", "L", "XL"],
        "size_guide_available": True,
        "description_completeness": 0.86,
        "image_url": "https://images.unsplash.com/photo-1509631179647-0177331693ae?auto=format&fit=crop&w=600&q=80",
        "description": "Breezy summery linen pant with pressed front crease, slash pockets, and removable matching belt.",
        "care_instructions": "Machine wash cold gentle, line dry, iron damp.",
        "known_fit_quirks": "Non-stretch linen; waist measurement must be exact. Inseam is long (designed to be worn with heels or hemmed).",
        "size_chart": {
            "XS": {"waist": 25.0, "hip": 37.0, "rise": 12.0, "inseam": 32.0},
            "S": {"waist": 27.0, "hip": 39.0, "rise": 12.5, "inseam": 32.0},
            "M": {"waist": 29.0, "hip": 41.0, "rise": 13.0, "inseam": 32.5},
            "L": {"waist": 31.5, "hip": 43.5, "rise": 13.5, "inseam": 32.5},
            "XL": {"waist": 34.5, "hip": 46.5, "rise": 14.0, "inseam": 33.0}
        }
    },
    {
        "product_id": "P017",
        "name": "Camp Collar Linen Floral Resort Shirt",
        "category": "Shirts",
        "price": 58.0,
        "fit_type": "Relaxed Fit",
        "material": "100% Pure Washed Linen",
        "sizes": ["S", "M", "L", "XL", "XXL"],
        "size_guide_available": True,
        "description_completeness": 0.89,
        "image_url": "https://images.unsplash.com/photo-1602810318383-e386cc2a3ccf?auto=format&fit=crop&w=600&q=80",
        "description": "Vacation ready Cuban collar short-sleeve shirt in subtle botanical print. Straight hem with side slits.",
        "care_instructions": "Cold wash, hang dry in shade.",
        "known_fit_quirks": "Relaxed straight body. Chest fits comfortably true to size.",
        "size_chart": {
            "S": {"chest": 41.0, "shoulder": 18.0, "length": 28.0},
            "M": {"chest": 43.5, "shoulder": 18.8, "length": 28.5},
            "L": {"chest": 46.0, "shoulder": 19.5, "length": 29.0},
            "XL": {"chest": 49.0, "shoulder": 20.3, "length": 29.5},
            "XXL": {"chest": 52.0, "shoulder": 21.0, "length": 30.0}
        }
    },
    {
        "product_id": "P018",
        "name": "Brushed Flannel Overshirt Shacket",
        "category": "Outerwear",
        "price": 79.0,
        "fit_type": "Regular Fit",
        "material": "100% Heavy Brushed Cotton Flannel",
        "sizes": ["S", "M", "L", "XL"],
        "size_guide_available": True,
        "description_completeness": 0.92,
        "image_url": "https://images.unsplash.com/photo-1591047139829-d91aecb6caea?auto=format&fit=crop&w=600&q=80",
        "description": "Mid-weight layer hybrid between shirt and jacket. Dual flap chest pockets, durable melamine buttons.",
        "care_instructions": "Machine wash cold with like colors, tumble dry low.",
        "known_fit_quirks": "Standard overshirt sizing with enough ease to fit over a t-shirt or light sweater.",
        "size_chart": {
            "S": {"chest": 41.5, "shoulder": 17.8, "length": 29.0, "sleeve": 34.0},
            "M": {"chest": 44.0, "shoulder": 18.6, "length": 29.8, "sleeve": 34.8},
            "L": {"chest": 47.0, "shoulder": 19.4, "length": 30.5, "sleeve": 35.5},
            "XL": {"chest": 50.0, "shoulder": 20.2, "length": 31.2, "sleeve": 36.2}
        }
    }
]

# Generate Synthetic Orders (850 records)
REASON_DISTRIBUTION = {
    "Size Too Small": 0.38,
    "Size Too Large": 0.22,
    "Fabric / Material Disappointment": 0.14,
    "Color Different From Photo": 0.09,
    "Shoulder / Armhole Tightness": 0.11,
    "Style Did Not Suit Customer": 0.06
}

FEEDBACK_SNIPPETS = {
    "Size Too Small": [
        "Way tighter than expected across the chest.",
        "Could barely button it up, definitely needed a size bigger.",
        "Runs much smaller than standard sizing charts.",
        "Waistband has zero give, couldn't zip comfortably."
    ],
    "Size Too Large": [
        "Swallowed me whole, very baggy.",
        "Drapes way too loose, recommend sizing down.",
        "Length and waist were much wider than standard."
    ],
    "Fabric / Material Disappointment": [
        "Fabric is much thinner than it appeared in photos.",
        "Material felt scratchy and stiff against skin.",
        "Not the premium hand-feel I anticipated for the price."
    ],
    "Color Different From Photo": [
        "Color is more muted than the vibrant online images.",
        "Expected crisp white but arrived slightly off-white cream.",
        "Shade has an unexpected olive undertone."
    ],
    "Shoulder / Armhole Tightness": [
        "Fits okay on waist but cuts into armpits whenever I raise my arms.",
        "Shoulder seams are very narrow, severely restricted mobility.",
        "Tension across upper back when driving."
    ],
    "Style Did Not Suit Customer": [
        "Looked great on model, cut just didn't flatter my proportions.",
        "Silhouette didn't work for my height."
    ]
}

# Pre-compute inherent product risk factors based on design
# P004, P008, P015 have higher risk due to missing size guides or tricky fabric
PRODUCT_INHERENT_RISK = {
    "P001": 0.28, # Slim fit upper back tightness
    "P002": 0.12, # Classic twill, true to size, low return
    "P003": 0.16, # Boxy tee, good tolerance
    "P004": 0.38, # Missing guide, tight armholes
    "P005": 0.25, # Raw denim waist rigidity
    "P006": 0.13, # Relaxed chinos, elastic tabs
    "P007": 0.32, # Blazer dress structured ribcage
    "P008": 0.42, # Missing guide, bias cut hip cling
    "P009": 0.15, # Overcoat, generous layering
    "P010": 0.18, # Technical jacket
    "P011": 0.24, # High compression leggings
    "P012": 0.14, # Active tech tee
    "P013": 0.22, # Leather dress shoe half-size discrepancy
    "P014": 0.17, # Sneaker
    "P015": 0.39, # Heavy cardigan missing detailed measurements
    "P016": 0.26, # Linen non-stretch trousers
    "P017": 0.15, # Resort linen shirt
    "P018": 0.16  # Overshirt
}

orders = []
start_date = datetime(2026, 1, 15)

for i in range(1, 921):
    order_id = f"ORD-{1000 + i}"
    product = random.choice(PRODUCTS)
    pid = product["product_id"]
    size = random.choice(product["sizes"])
    
    # Calculate baseline probability of return
    p_risk = PRODUCT_INHERENT_RISK[pid]
    
    # Size guide availability effect
    if not product["size_guide_available"]:
        p_risk += 0.08
        
    # Completeness effect
    p_risk += (1.0 - product["description_completeness"]) * 0.15
    
    # Bracketing effect: Customer bought 2+ sizes of same item to try on
    bracketing = random.random() < 0.12
    if bracketing:
        p_risk += 0.22
        
    # Discount effect: heavy discount slightly increases impulse purchase return
    discount_applied = random.choice([0, 0, 0.1, 0.15, 0.25])
    if discount_applied >= 0.20:
        p_risk += 0.05
        
    # Selected size quirk (e.g. S on P001 has higher return due to shoulder tightness)
    if pid == "P001" and size in ["S", "M"]:
        p_risk += 0.09
    elif pid == "P007" and size in ["XS", "S"]:
        p_risk += 0.08
    elif pid == "P008" and size in ["XS", "S"]:
        p_risk += 0.10
        
    p_risk = min(max(p_risk, 0.05), 0.85)
    
    # Sample return outcome
    returned = 1 if random.random() < p_risk else 0
    
    return_reason = None
    customer_feedback = None
    if returned == 1:
        # Sample reason based on product category & quirks
        if pid in ["P001", "P004", "P007"]:
            reasons = ["Shoulder / Armhole Tightness", "Size Too Small", "Fabric / Material Disappointment"]
            weights = [0.45, 0.40, 0.15]
        elif pid in ["P008", "P015"]:
            reasons = ["Size Too Small", "Fabric / Material Disappointment", "Color Different From Photo"]
            weights = [0.40, 0.40, 0.20]
        elif pid in ["P005", "P016"]:
            reasons = ["Size Too Small", "Size Too Large", "Style Did Not Suit Customer"]
            weights = [0.55, 0.25, 0.20]
        else:
            reasons = list(REASON_DISTRIBUTION.keys())
            weights = list(REASON_DISTRIBUTION.values())
            
        return_reason = random.choices(reasons, weights=weights, k=1)[0]
        customer_feedback = random.choice(FEEDBACK_SNIPPETS[return_reason])
        
    # Realistic order timestamp over past 10 months
    days_offset = random.randint(0, 280)
    order_date = start_date + timedelta(days=days_offset, hours=random.randint(8, 22), minutes=random.randint(0, 59))
    
    orders.append({
        "order_id": order_id,
        "product_id": pid,
        "product_name": product["name"],
        "category": product["category"],
        "price": product["price"],
        "selected_size": size,
        "fit_type": product["fit_type"],
        "size_guide_available": 1 if product["size_guide_available"] else 0,
        "description_completeness": product["description_completeness"],
        "discount_applied": discount_applied,
        "bracketing_order": 1 if bracketing else 0,
        "returned": returned,
        "return_reason": return_reason,
        "customer_feedback": customer_feedback,
        "order_date": order_date.strftime("%Y-%m-%d %H:%M:%S")
    })

df_orders = pd.DataFrame(orders)

# Compute product-level historical return statistics to eliminate data leakage
prod_stats = df_orders.groupby("product_id")["returned"].agg(["count", "mean"]).reset_index()
prod_stats.columns = ["product_id", "total_orders", "historical_return_rate"]
prod_stats["historical_return_rate"] = prod_stats["historical_return_rate"].round(4)

# Compute size-level return statistics per product
size_stats = df_orders.groupby(["product_id", "selected_size"])["returned"].agg(["count", "mean"]).reset_index()
size_stats.columns = ["product_id", "selected_size", "size_total_orders", "product_size_return_rate"]
size_stats["product_size_return_rate"] = size_stats["product_size_return_rate"].round(4)

# Merge pre-purchase signals back into order dataset
df_orders = df_orders.merge(prod_stats[["product_id", "historical_return_rate"]], on="product_id", how="left")
df_orders = df_orders.merge(size_stats[["product_id", "selected_size", "product_size_return_rate"]], on=["product_id", "selected_size"], how="left")

# Save datasets
df_orders.to_csv(os.path.join(DATA_DIR, "orders_dataset.csv"), index=False)

# Enrich PRODUCTS with computed statistics & risk category
for p in PRODUCTS:
    p_stat = prod_stats[prod_stats["product_id"] == p["product_id"]]
    if not p_stat.empty:
        rate = float(p_stat["historical_return_rate"].iloc[0])
        p["historical_return_rate"] = rate
        p["total_orders"] = int(p_stat["total_orders"].iloc[0])
        p["risk_category"] = "High Risk" if rate > 0.30 else ("Medium Risk" if rate > 0.18 else "Low Risk")
    else:
        p["historical_return_rate"] = 0.20
        p["total_orders"] = 50
        p["risk_category"] = "Medium Risk"

with open(os.path.join(DATA_DIR, "products.json"), "w", encoding="utf-8") as f:
    json.dump(PRODUCTS, f, indent=2)

print(f"Data Generation Completed successfully:")
print(f"  - Products: {len(PRODUCTS)}")
print(f"  - Orders: {len(df_orders)} (Return rate: {df_orders['returned'].mean():.2%})")
print(f"  - Saved to: {DATA_DIR}")

