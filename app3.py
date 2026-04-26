import random
import string
from flask import Flask, render_template_string, jsonify
import json

app = Flask(__name__)

# Track current state to simulate realistic changes over time
class SiteState:
    def __init__(self):
        self.version = 1
        self.css_version = 1  # CSS naming version
        self.json_version = 1  # JSON structure version
        self.unit_version = 1  # Price unit version
        self.punct_version = 1  # Punctuation version
        self.dom_version = 1  # DOM structure version
        
    def trigger_change(self):
        """Randomly trigger one type of breaking change"""
        change_type = random.choice([
            'css_rename',
            'json_nesting', 
            'unit_drift',
            'punctuation_drift',
            'shadow_dom',
            'none'  # Sometimes no change
        ])
        
        if change_type == 'css_rename':
            self.css_version += 1
        elif change_type == 'json_nesting':
            self.json_version += 1
        elif change_type == 'unit_drift':
            self.unit_version += 1
        elif change_type == 'punctuation_drift':
            self.punct_version += 1
        elif change_type == 'shadow_dom':
            self.dom_version += 1
            
        self.version += 1
        return change_type

state = SiteState()

# ============================================================================
# CSS SELECTOR VARIATIONS - Realistic naming changes that break scrapers
# ============================================================================

CSS_VARIATIONS = {
    'price': {
        1: 'price-color',           # Initial (common pattern)
        2: 'product-price',          # First change (still semantic)
        3: 'item-cost',              # Second change (different wording)
        4: 'price-display',          # Third change
        5: 'currency-value',         # Fourth change (different concept)
        6: 'cost-amount',            # Fifth change
        7: 'price-tag',              # Sixth change
        8: 'product-cost-display',   # Seventh change (compound)
    },
    'title': {
        1: 'product-title',          # Initial
        2: 'item-name',              # Change to different naming
        3: 'product-heading',        # Change to structural name
        4: 'title-text',             # Generic name
        5: 'product-name-display',   # Verbose name
        6: 'item-title-header',      # Compound name
        7: 'product-label',          # Different concept
        8: 'name-heading',           # Mixed approach
    },
    'stock': {
        1: 'availability',           # Initial
        2: 'stock-status',           # Clearer naming
        3: 'in-stock-badge',         # More specific
        4: 'availability-info',      # Added suffix
        5: 'stock-indicator',        # Different wording
        6: 'product-availability',   # Prefixed
        7: 'inventory-status',       # Domain-specific term
        8: 'stock-level',            # Different aspect
    }
}

# ============================================================================
# JSON STRUCTURE VARIATIONS - Progressive nesting that breaks key access
# ============================================================================

def get_json_structure(version, price_value, currency, title, stock):
    """Generate JSON with different nesting levels based on version"""
    
    if version == 1:
        # Flat structure (initial state)
        return {
            "title": title,
            "price": price_value,
            "currency": currency,
            "stock": stock,
            "timestamp": "2026-02-16T10:00:00Z"
        }
    
    elif version == 2:
        # First nesting: price becomes object
        return {
            "title": title,
            "pricing": {
                "amount": price_value,
                "currency": currency
            },
            "stock": stock,
            "timestamp": "2026-02-16T10:00:00Z"
        }
    
    elif version == 3:
        # Second nesting: stock becomes object
        return {
            "title": title,
            "pricing": {
                "amount": price_value,
                "currency": currency
            },
            "availability": {
                "status": stock,
                "quantity": 100
            },
            "timestamp": "2026-02-16T10:00:00Z"
        }
    
    elif version == 4:
        # Third nesting: everything under 'product'
        return {
            "product": {
                "name": title,
                "pricing": {
                    "amount": price_value,
                    "currency": currency
                },
                "availability": {
                    "status": stock,
                    "quantity": 100
                }
            },
            "timestamp": "2026-02-16T10:00:00Z"
        }
    
    elif version == 5:
        # Fourth nesting: deep nesting with display objects
        return {
            "product": {
                "details": {
                    "name": title
                },
                "pricing": {
                    "display": {
                        "amount": price_value,
                        "currency": currency
                    }
                },
                "availability": {
                    "stock": {
                        "status": stock,
                        "count": 100
                    }
                }
            },
            "metadata": {
                "timestamp": "2026-02-16T10:00:00Z"
            }
        }
    
    else:
        # Even deeper nesting (version 6+)
        return {
            "data": {
                "product": {
                    "information": {
                        "title": {
                            "text": title
                        }
                    },
                    "cost": {
                        "pricing": {
                            "value": {
                                "amount": price_value,
                                "currency": currency
                            }
                        }
                    },
                    "inventory": {
                        "availability": {
                            "stock": {
                                "status": stock
                            }
                        }
                    }
                }
            }
        }

# ============================================================================
# UNIT DRIFT VARIATIONS - Price format changes that break parsing
# ============================================================================

UNIT_FORMATS = {
    1: {"value": 300.00, "format": "${:.2f}"},           # USD standard: $300.00
    2: {"value": 300.00, "format": "USD {:.2f}"},        # USD prefix: USD 300.00
    3: {"value": 255.00, "format": "£{:.2f}"},           # GBP: £255.00
    4: {"value": 280.00, "format": "{:.2f} EUR"},        # EUR suffix: 280.00 EUR
    5: {"value": 300.00, "format": "$ {:.2f} USD"},      # Spaced: $ 300.00 USD
    6: {"value": 33000, "format": "¥{:,.0f}"},           # JPY (no decimals): ¥33,000
    7: {"value": 300.00, "format": "{:,.2f} dollars"},   # Spelled out: 300.00 dollars
    8: {"value": 300, "format": "{:d} USD"},             # Integer: 300 USD
}

# ============================================================================
# PUNCTUATION DRIFT VARIATIONS - Delimiter changes that break regex parsing
# ============================================================================

PUNCTUATION_FORMATS = {
    1: "In Stock",              # Initial: space separated
    2: "In-Stock",              # Hyphenated
    3: "In_Stock",              # Underscored
    4: "InStock",               # CamelCase
    5: "in.stock",              # Dotted, lowercase
    6: "IN STOCK",              # UPPERCASE with space
    7: "In|Stock",              # Pipe separated
    8: "In::Stock",             # Double colon
}

# ============================================================================
# HTML TEMPLATES - Different DOM structures
# ============================================================================

# Standard DOM Template
STANDARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>AegisFlow Product Catalog - Version {{ version }}</title>
    <meta name="change-type" content="{{ change_type }}">
    <style>
        body { font-family: sans-serif; margin: 40px; background: #f4f4f9; }
        .container { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .{{ price_class }} { color: #d9534f; font-weight: bold; font-size: 1.2em; }
        .{{ title_class }} { color: #333; font-size: 1.5em; margin-bottom: 10px; }
        .{{ stock_class }} { color: green; font-weight: bold; }
        .meta-info { background: #f0f0f0; padding: 10px; margin-top: 20px; border-radius: 4px; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <h1>AegisFlow Product Catalog</h1>
        <p><strong>Test Page Version:</strong> {{ version }} | <strong>CSS Version:</strong> {{ css_version }} | <strong>JSON Version:</strong> {{ json_version }}</p>
        <p><em>This page simulates real-world breaking changes for scraper testing</em></p>
        <hr>
        
        <div class="product-item" data-product-id="aegisflow-001">
            <div class="{{ title_class }}" data-field="title">
                AegisFlow: Autonomous Remediation Framework
            </div>
            
            <p>Status: <span class="{{ stock_class }}" data-field="stock">{{ stock_text }}</span></p>
            
            <div class="price-wrapper">
                Price: <span class="{{ price_class }}" data-field="price">{{ price_text }}</span>
            </div>
            
            <div class="meta-info">
                <strong>Current Breaking Change:</strong> {{ change_type }}<br>
                <strong>Scraper Challenge:</strong> {{ challenge_description }}
            </div>
        </div>
        
        <div class="api-info" style="margin-top: 30px; padding: 15px; background: #e8f4f8; border-radius: 4px;">
            <h3>API Endpoint Available</h3>
            <p>GET <code>/api/product</code> - Returns JSON with current structure (JSON version {{ json_version }})</p>
            <p><a href="/api/product" target="_blank">View JSON API</a></p>
        </div>
    </div>
</body>
</html>
"""

# Shadow DOM Template - Content hidden in Shadow DOM
SHADOW_DOM_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>AegisFlow Product Catalog - Shadow DOM Version {{ version }}</title>
    <meta name="change-type" content="shadow_dom">
    <style>
        body { font-family: sans-serif; margin: 40px; background: #f4f4f9; }
        .container { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .meta-info { background: #f0f0f0; padding: 10px; margin-top: 20px; border-radius: 4px; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <h1>AegisFlow Product Catalog</h1>
        <p><strong>Test Page Version:</strong> {{ version }} | <strong>DOM Version:</strong> {{ dom_version }}</p>
        <p><em>⚠️ Product details now inside Shadow DOM - Traditional scrapers will fail!</em></p>
        <hr>
        
        <!-- Shadow DOM Host -->
        <product-widget id="aegisflow-widget"></product-widget>
        
        <div class="meta-info">
            <strong>Current Breaking Change:</strong> Shadow DOM Move<br>
            <strong>Scraper Challenge:</strong> Product details moved into Shadow DOM. Regular selectors won't work. Need <code>shadowRoot</code> access.
        </div>
        
        <div class="api-info" style="margin-top: 30px; padding: 15px; background: #e8f4f8; border-radius: 4px;">
            <h3>API Endpoint Available</h3>
            <p>GET <code>/api/product</code> - Returns JSON (fallback for Shadow DOM)</p>
            <p><a href="/api/product" target="_blank">View JSON API</a></p>
        </div>
    </div>
    
    <script>
        // Define custom element with Shadow DOM
        class ProductWidget extends HTMLElement {
            constructor() {
                super();
                const shadow = this.attachShadow({mode: 'open'});
                
                shadow.innerHTML = `
                    <style>
                        .product-details { padding: 20px; background: #fff; border: 1px solid #ddd; border-radius: 8px; }
                        .product-title { color: #333; font-size: 1.5em; margin-bottom: 10px; font-weight: bold; }
                        .product-price { color: #d9534f; font-weight: bold; font-size: 1.2em; }
                        .product-stock { color: green; font-weight: bold; }
                    </style>
                    <div class="product-details">
                        <div class="product-title" data-field="title">
                            AegisFlow: Autonomous Remediation Framework
                        </div>
                        <p>Status: <span class="product-stock" data-field="stock">{{ stock_text }}</span></p>
                        <div>
                            Price: <span class="product-price" data-field="price">{{ price_text }}</span>
                        </div>
                    </div>
                `;
            }
        }
        
        customElements.define('product-widget', ProductWidget);
    </script>
</body>
</html>
"""

# ============================================================================
# FLASK ROUTES
# ============================================================================

@app.route('/')
def index():
    """Main page that randomly changes structure on each load"""
    
    # Occasionally trigger a breaking change (30% chance)
    change_type = 'none'
    if random.random() < 0.3:
        change_type = state.trigger_change()
    
    # Get current CSS class names based on version
    price_class = CSS_VARIATIONS['price'].get(state.css_version, CSS_VARIATIONS['price'][1])
    title_class = CSS_VARIATIONS['title'].get(state.css_version, CSS_VARIATIONS['title'][1])
    stock_class = CSS_VARIATIONS['stock'].get(state.css_version, CSS_VARIATIONS['stock'][1])
    
    # Get current price format based on version
    unit_format = UNIT_FORMATS.get(state.unit_version, UNIT_FORMATS[1])
    price_text = unit_format['format'].format(unit_format['value'])
    
    # Get current stock punctuation based on version
    stock_text = PUNCTUATION_FORMATS.get(state.punct_version, PUNCTUATION_FORMATS[1])
    
    # Get challenge description
    challenge_descriptions = {
        'css_rename': f'CSS classes changed (price: {price_class}, title: {title_class})',
        'json_nesting': f'JSON structure nested to level {state.json_version}',
        'unit_drift': f'Price format changed to: {price_text}',
        'punctuation_drift': f'Stock status punctuation changed to: {stock_text}',
        'shadow_dom': 'Product moved into Shadow DOM',
        'none': 'No change (stable state)'
    }
    
    challenge_description = challenge_descriptions.get(change_type, 'Unknown change')
    
    # Use Shadow DOM template for shadow_dom version
    if state.dom_version > 1 and change_type == 'shadow_dom':
        template = SHADOW_DOM_TEMPLATE
    else:
        template = STANDARD_TEMPLATE
    
    return render_template_string(
        template,
        version=state.version,
        css_version=state.css_version,
        json_version=state.json_version,
        dom_version=state.dom_version,
        price_class=price_class,
        title_class=title_class,
        stock_class=stock_class,
        price_text=price_text,
        stock_text=stock_text,
        change_type=change_type,
        challenge_description=challenge_description
    )

@app.route('/api/product')
def api_product():
    """JSON API endpoint with structure that changes based on version"""
    
    # Get current values
    unit_format = UNIT_FORMATS.get(state.unit_version, UNIT_FORMATS[1])
    price_value = unit_format['value']
    currency = "USD"  # Simplified for JSON
    
    stock_text = PUNCTUATION_FORMATS.get(state.punct_version, PUNCTUATION_FORMATS[1])
    title = "AegisFlow: Autonomous Remediation Framework"
    
    # Generate JSON structure based on current version
    product_data = get_json_structure(
        state.json_version,
        price_value,
        currency,
        title,
        stock_text
    )
    
    # Add metadata
    response = {
        "version": state.version,
        "json_version": state.json_version,
        "css_version": state.css_version,
        "data": product_data
    }
    
    return jsonify(response)

@app.route('/api/reset')
def api_reset():
    """Reset state to version 1 (useful for testing)"""
    global state
    state = SiteState()
    return jsonify({
        "status": "reset",
        "message": "All versions reset to 1"
    })

@app.route('/api/force-change/<change_type>')
def api_force_change(change_type):
    """Force a specific type of change (for controlled testing)"""
    
    valid_changes = ['css_rename', 'json_nesting', 'unit_drift', 'punctuation_drift', 'shadow_dom']
    
    if change_type not in valid_changes:
        return jsonify({
            "error": "Invalid change type",
            "valid_types": valid_changes
        }), 400
    
    if change_type == 'css_rename':
        state.css_version += 1
    elif change_type == 'json_nesting':
        state.json_version += 1
    elif change_type == 'unit_drift':
        state.unit_version += 1
    elif change_type == 'punctuation_drift':
        state.punct_version += 1
    elif change_type == 'shadow_dom':
        state.dom_version += 1
    
    state.version += 1
    
    return jsonify({
        "status": "changed",
        "change_type": change_type,
        "new_version": state.version,
        "css_version": state.css_version,
        "json_version": state.json_version,
        "unit_version": state.unit_version,
        "punct_version": state.punct_version,
        "dom_version": state.dom_version
    })

@app.route('/api/status')
def api_status():
    """Get current state information"""
    
    return jsonify({
        "version": state.version,
        "css_version": state.css_version,
        "json_version": state.json_version,
        "unit_version": state.unit_version,
        "punct_version": state.punct_version,
        "dom_version": state.dom_version,
        "current_selectors": {
            "price": CSS_VARIATIONS['price'].get(state.css_version),
            "title": CSS_VARIATIONS['title'].get(state.css_version),
            "stock": CSS_VARIATIONS['stock'].get(state.css_version)
        }
    })

if __name__ == '__main__':
    print("="*70)
    print("AegisFlow Breaking Changes Test Server")
    print("="*70)
    print("\nAvailable endpoints:")
    print("  http://localhost:5000/                    - Main product page (random changes)")
    print("  http://localhost:5000/api/product         - JSON API (changing structure)")
    print("  http://localhost:5000/api/status          - Current state info")
    print("  http://localhost:5000/api/reset           - Reset all versions to 1")
    print("  http://localhost:5000/api/force-change/css_rename")
    print("  http://localhost:5000/api/force-change/json_nesting")
    print("  http://localhost:5000/api/force-change/unit_drift")
    print("  http://localhost:5000/api/force-change/punctuation_drift")
    print("  http://localhost:5000/api/force-change/shadow_dom")
    print("\nBreaking changes implemented:")
    print("  ✓ CSS Rename - Realistic class name evolution")
    print("  ✓ JSON Nesting - Progressive API structure changes")
    print("  ✓ Unit Drift - Currency/format variations")
    print("  ✓ Punctuation Drift - Delimiter changes")
    print("  ✓ Shadow DOM Move - Content in Shadow DOM")
    print("\nServer starting on http://localhost:5000")
    print("="*70)
    
    app.run(debug=True, port=5000)