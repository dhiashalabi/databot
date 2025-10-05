DROP TABLE IF EXISTS invoice_item CASCADE;
DROP TABLE IF EXISTS invoice CASCADE;
DROP TABLE IF EXISTS sale CASCADE;
DROP TABLE IF EXISTS product CASCADE;
DROP TABLE IF EXISTS category CASCADE;
DROP TABLE IF EXISTS customer CASCADE;
DROP TABLE IF EXISTS "user" CASCADE;

CREATE TABLE "user" (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_admin BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE permissions (
    id SERIAL PRIMARY KEY,
    code VARCHAR(100) UNIQUE NOT NULL, -- e.g. "ai.use", "mcp.sales.view", "mcp.product.edit"
    description TEXT,
    category VARCHAR(50), -- optional: "AI", "MCP", "System"
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE role_permissions (
    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    permission_id INTEGER REFERENCES permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

CREATE TABLE user_roles (
    user_id UUID REFERENCES "user"(id) ON DELETE CASCADE,
    role_id INTEGER REFERENCES roles(id) ON DELETE CASCADE,
    PRIMARY KEY (user_id, role_id)
);

CREATE TABLE tool_permissions (
    id SERIAL PRIMARY KEY,
    tool_name VARCHAR(100) NOT NULL, -- e.g. "sales_tool", "charts_tool"
    permission_code VARCHAR(100) REFERENCES permissions(code),
    is_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE customer (
    id SERIAL PRIMARY KEY,
    customer_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    company VARCHAR(255),
    address VARCHAR(500),
    city VARCHAR(100),
    country VARCHAR(100),
    customer_type VARCHAR(50) DEFAULT 'retail',
    credit_limit DECIMAL(10, 2) DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE category (
    id SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    parent_category_id INTEGER REFERENCES category(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE product (
    id SERIAL PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    sku VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    category_id INTEGER REFERENCES category(id) ON DELETE SET NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    cost_price DECIMAL(10, 2),
    stock_quantity INTEGER DEFAULT 0,
    reorder_level INTEGER DEFAULT 10,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE invoice (
    id SERIAL PRIMARY KEY,
    invoice_number VARCHAR(50) UNIQUE NOT NULL,
    customer_id INTEGER NOT NULL REFERENCES customer(id) ON DELETE RESTRICT,
    invoice_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    due_date TIMESTAMP,
    subtotal DECIMAL(12, 2) NOT NULL DEFAULT 0,
    tax_amount DECIMAL(12, 2) DEFAULT 0,
    discount_amount DECIMAL(12, 2) DEFAULT 0,
    total_amount DECIMAL(12, 2) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    payment_method VARCHAR(50),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE invoice_item (
    id SERIAL PRIMARY KEY,
    invoice_id INTEGER NOT NULL REFERENCES invoice(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL REFERENCES product(id) ON DELETE RESTRICT,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price DECIMAL(10, 2) NOT NULL,
    discount_percent DECIMAL(5, 2) DEFAULT 0,
    line_total DECIMAL(12, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE sale (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customer(id) ON DELETE SET NULL,
    product_id INTEGER REFERENCES product(id) ON DELETE SET NULL,
    invoice_id INTEGER REFERENCES invoice(id) ON DELETE SET NULL,
    product_name VARCHAR(255) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    quantity INTEGER DEFAULT 1,
    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    customer_name VARCHAR(255),
    category VARCHAR(100),
    payment_status VARCHAR(50) DEFAULT 'completed',
    sales_channel VARCHAR(50) DEFAULT 'online',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_email ON "user"(email);
CREATE INDEX idx_user_username ON "user"(username);
CREATE INDEX idx_customer_email ON customer(email);
CREATE INDEX idx_customer_name ON customer(customer_name);
CREATE INDEX idx_product_sku ON product(sku);
CREATE INDEX idx_product_category ON product(category_id);
CREATE INDEX idx_invoice_customer ON invoice(customer_id);
CREATE INDEX idx_invoice_date ON invoice(invoice_date);
CREATE INDEX idx_invoice_status ON invoice(status);
CREATE INDEX idx_invoice_item_invoice ON invoice_item(invoice_id);
CREATE INDEX idx_invoice_item_product ON invoice_item(product_id);
CREATE INDEX idx_sale_date ON sale(sale_date);
CREATE INDEX idx_sale_customer ON sale(customer_id);
CREATE INDEX idx_sale_product ON sale(product_id);

INSERT INTO category (category_name, description, parent_category_id) VALUES
('Electronics', 'Electronic devices and gadgets', NULL),
('Computers', 'Desktop and laptop computers', 1),
('Accessories', 'Computer and electronic accessories', 1),
('Office Supplies', 'Office furniture and supplies', NULL),
('Furniture', 'Office furniture', 4),
('Stationery', 'Writing and paper supplies', 4),
('Software', 'Software and digital products', NULL),
('Networking', 'Network equipment and accessories', 1),
('Peripherals', 'Input and output devices', 1),
('Storage', 'Data storage devices', 1),
('Audio', 'Audio equipment', 1),
('Video', 'Video equipment and displays', 1),
('Mobile', 'Mobile devices and accessories', 1),
('Gaming', 'Gaming equipment', 1),
('Security', 'Security systems and software', 1);

INSERT INTO product (product_name, sku, description, category_id, unit_price, cost_price, stock_quantity, reorder_level) VALUES
('Laptop Pro 15"', 'LPT-PRO-15', 'Professional laptop with 16GB RAM', 2, 1299.99, 950.00, 45, 10),
('Desktop Workstation', 'DSK-WRK-01', 'High-performance desktop computer', 2, 1899.99, 1400.00, 30, 8),
('Laptop Ultra 13"', 'LPT-ULT-13', 'Ultralight portable laptop', 2, 999.99, 750.00, 60, 15),
('Gaming Desktop', 'DSK-GAM-01', 'Gaming desktop with RTX graphics', 14, 2499.99, 1800.00, 20, 5),

('Wireless Mouse Pro', 'MSE-WLS-01', 'Ergonomic wireless mouse', 9, 29.99, 12.00, 200, 50),
('Mechanical Keyboard RGB', 'KBD-MCH-RGB', 'RGB backlit mechanical keyboard', 9, 129.99, 65.00, 150, 30),
('USB-C Cable 2m', 'CBL-USC-2M', 'High-speed USB-C cable', 3, 19.99, 5.00, 500, 100),
('Webcam HD Pro', 'WBC-HD-PRO', '1080p HD webcam with microphone', 9, 79.99, 40.00, 120, 25),
('Wireless Headset', 'HDS-WLS-01', 'Noise-canceling wireless headset', 11, 149.99, 75.00, 80, 20),
('USB Hub 7-Port', 'HUB-USB-7P', '7-port powered USB hub', 3, 39.99, 18.00, 180, 40),

('Monitor 27" 4K', 'MON-27-4K', '27-inch 4K UHD monitor', 12, 399.99, 250.00, 70, 15),
('Monitor 24" FHD', 'MON-24-FHD', '24-inch Full HD monitor', 12, 199.99, 120.00, 100, 20),
('Dual Monitor Stand', 'STD-MON-D2', 'Adjustable dual monitor stand', 3, 89.99, 40.00, 60, 15),

('External SSD 1TB', 'SSD-EXT-1T', 'Portable external SSD 1TB', 10, 129.99, 70.00, 150, 30),
('External HDD 4TB', 'HDD-EXT-4T', 'External hard drive 4TB', 10, 99.99, 55.00, 120, 25),
('USB Flash Drive 128GB', 'USB-FLS-128', '128GB USB 3.0 flash drive', 10, 24.99, 10.00, 300, 60),

('WiFi Router AC', 'RTR-WIFI-AC', 'Dual-band WiFi router', 8, 79.99, 40.00, 90, 20),
('Network Switch 8-Port', 'SWT-NET-8P', 'Gigabit network switch', 8, 49.99, 25.00, 110, 25),
('Ethernet Cable 5m', 'CBL-ETH-5M', 'Cat6 ethernet cable 5m', 8, 12.99, 4.00, 400, 80),

('Office Chair Executive', 'CHR-EXE-01', 'Ergonomic executive chair', 5, 299.99, 150.00, 50, 10),
('Standing Desk Adjustable', 'DSK-STD-ADJ', 'Electric adjustable standing desk', 5, 599.99, 350.00, 35, 8),
('Desk Lamp LED', 'LMP-DSK-LED', 'Adjustable LED desk lamp', 5, 45.99, 20.00, 140, 30),
('Monitor Riser', 'RSR-MON-01', 'Adjustable monitor riser with storage', 5, 39.99, 18.00, 100, 25),

('Notebook Set Premium', 'NTB-SET-PRM', 'Set of 5 premium notebooks', 6, 24.99, 10.00, 250, 50),
('Pen Pack Gel 12pc', 'PEN-GEL-12', 'Pack of 12 gel pens assorted colors', 6, 14.99, 6.00, 400, 80),
('Sticky Notes Combo', 'STK-CMB-01', 'Sticky notes combo pack', 6, 9.99, 4.00, 500, 100),
('Desk Organizer', 'ORG-DSK-01', 'Multi-compartment desk organizer', 6, 29.99, 12.00, 150, 30),

('Productivity Suite License', 'SFW-PRO-LIC', 'Annual productivity software license', 7, 149.99, 50.00, 999, 50),
('Antivirus Pro 1-Year', 'SFW-AV-1Y', '1-year antivirus protection', 15, 59.99, 20.00, 999, 50),
('Photo Editor Pro', 'SFW-PHT-PRO', 'Professional photo editing software', 7, 299.99, 100.00, 999, 50),

('Gaming Mouse RGB', 'MSE-GAM-RGB', 'High-DPI gaming mouse with RGB', 14, 69.99, 30.00, 120, 25),
('Gaming Keyboard Mechanical', 'KBD-GAM-MCH', 'Mechanical gaming keyboard', 14, 159.99, 80.00, 90, 20),
('Gaming Headset 7.1', 'HDS-GAM-71', '7.1 surround gaming headset', 14, 99.99, 50.00, 110, 25),
('Gaming Chair', 'CHR-GAM-01', 'Ergonomic gaming chair', 14, 349.99, 180.00, 40, 10),

('Tablet 10" WiFi', 'TBL-10-WIFI', '10-inch WiFi tablet', 13, 399.99, 250.00, 70, 15),
('Phone Case Universal', 'CSE-PHN-UNI', 'Universal phone protective case', 13, 19.99, 6.00, 300, 60),
('Wireless Charger Pad', 'CHG-WLS-PAD', 'Fast wireless charging pad', 13, 34.99, 15.00, 200, 40),

('Security Camera WiFi', 'CAM-SEC-WIFI', 'WiFi security camera 1080p', 15, 89.99, 45.00, 85, 20),
('Smart Door Lock', 'LCK-SRT-01', 'Smart keyless door lock', 15, 199.99, 100.00, 55, 12),
('Password Manager 1-Year', 'SFW-PWD-1Y', '1-year password manager subscription', 15, 39.99, 10.00, 999, 50);

INSERT INTO customer (customer_name, email, phone, company, address, city, country, customer_type, credit_limit) VALUES
('John Smith', 'john.smith@email.com', '+1-555-0101', 'Tech Solutions Inc', '123 Main St', 'New York', 'USA', 'corporate', 10000.00),
('Sarah Johnson', 'sarah.j@email.com', '+1-555-0102', NULL, '456 Oak Ave', 'Los Angeles', 'USA', 'retail', 5000.00),
('Michael Brown', 'mbrown@company.com', '+1-555-0103', 'Brown Enterprises', '789 Pine Rd', 'Chicago', 'USA', 'wholesale', 25000.00),
('Emily Davis', 'emily.davis@email.com', '+1-555-0104', NULL, '321 Elm St', 'Houston', 'USA', 'retail', 3000.00),
('David Wilson', 'dwilson@email.com', '+1-555-0105', 'Wilson & Co', '654 Maple Dr', 'Phoenix', 'USA', 'corporate', 15000.00),
('Jessica Martinez', 'jessica.m@email.com', '+1-555-0106', NULL, '987 Cedar Ln', 'Philadelphia', 'USA', 'retail', 4000.00),
('James Anderson', 'j.anderson@business.com', '+1-555-0107', 'Anderson Corp', '147 Birch Ave', 'San Antonio', 'USA', 'corporate', 20000.00),
('Jennifer Taylor', 'jtaylor@email.com', '+1-555-0108', NULL, '258 Spruce St', 'San Diego', 'USA', 'retail', 3500.00),
('Robert Thomas', 'rthomas@email.com', '+1-555-0109', 'Thomas Industries', '369 Ash Rd', 'Dallas', 'USA', 'wholesale', 30000.00),
('Linda Jackson', 'linda.j@email.com', '+1-555-0110', NULL, '741 Willow Way', 'San Jose', 'USA', 'retail', 2500.00),
('Christopher White', 'cwhite@company.com', '+1-555-0111', 'White Tech', '852 Poplar Dr', 'Austin', 'USA', 'corporate', 12000.00),
('Mary Harris', 'mary.harris@email.com', '+1-555-0112', NULL, '963 Hickory Ln', 'Jacksonville', 'USA', 'retail', 4500.00),
('Daniel Martin', 'dmartin@email.com', '+1-555-0113', 'Martin Solutions', '159 Walnut St', 'Fort Worth', 'USA', 'wholesale', 18000.00),
('Patricia Thompson', 'pthompson@email.com', '+1-555-0114', NULL, '357 Chestnut Ave', 'Columbus', 'USA', 'retail', 3200.00),
('Matthew Garcia', 'mgarcia@business.com', '+1-555-0115', 'Garcia Group', '486 Sycamore Rd', 'San Francisco', 'USA', 'corporate', 22000.00),
('Elizabeth Martinez', 'emartinez@email.com', '+1-555-0116', NULL, '597 Magnolia Dr', 'Charlotte', 'USA', 'retail', 2800.00),
('Anthony Robinson', 'arobinson@email.com', '+1-555-0117', 'Robinson LLC', '618 Dogwood Ln', 'Indianapolis', 'USA', 'wholesale', 16000.00),
('Barbara Clark', 'bclark@email.com', '+1-555-0118', NULL, '729 Redwood Way', 'Seattle', 'USA', 'retail', 4200.00),
('Mark Rodriguez', 'mrodriguez@company.com', '+1-555-0119', 'Rodriguez Inc', '831 Sequoia St', 'Denver', 'USA', 'corporate', 14000.00),
('Susan Lewis', 'slewis@email.com', '+1-555-0120', NULL, '942 Cypress Ave', 'Boston', 'USA', 'retail', 3600.00),
('Paul Lee', 'plee@business.com', '+1-555-0121', 'Lee Enterprises', '153 Fir Rd', 'El Paso', 'USA', 'wholesale', 21000.00),
('Karen Walker', 'kwalker@email.com', '+1-555-0122', NULL, '264 Cedar Way', 'Nashville', 'USA', 'retail', 2900.00),
('Steven Hall', 'shall@email.com', '+1-555-0123', 'Hall Technologies', '375 Pine Dr', 'Detroit', 'USA', 'corporate', 17000.00),
('Nancy Allen', 'nallen@email.com', '+1-555-0124', NULL, '486 Oak Ln', 'Portland', 'USA', 'retail', 4100.00),
('Kevin Young', 'kyoung@company.com', '+1-555-0125', 'Young Corp', '597 Maple St', 'Las Vegas', 'USA', 'wholesale', 19000.00),
('Lisa Hernandez', 'lhernandez@email.com', '+1-555-0126', NULL, '618 Elm Ave', 'Louisville', 'USA', 'retail', 3300.00),
('Brian King', 'bking@email.com', '+1-555-0127', 'King Industries', '729 Birch Rd', 'Baltimore', 'USA', 'corporate', 13000.00),
('Betty Wright', 'bwright@email.com', '+1-555-0128', NULL, '831 Spruce Dr', 'Milwaukee', 'USA', 'retail', 2700.00),
('George Lopez', 'glopez@business.com', '+1-555-0129', 'Lopez Group', '942 Ash Ln', 'Albuquerque', 'USA', 'wholesale', 24000.00),
('Helen Scott', 'hscott@email.com', '+1-555-0130', NULL, '153 Willow Way', 'Tucson', 'USA', 'retail', 3900.00),
('Edward Green', 'egreen@email.com', '+1-555-0131', 'Green Solutions', '264 Poplar St', 'Fresno', 'USA', 'corporate', 11000.00),
('Sandra Adams', 'sadams@email.com', '+1-555-0132', NULL, '375 Hickory Ave', 'Sacramento', 'USA', 'retail', 3400.00),
('Ronald Baker', 'rbaker@company.com', '+1-555-0133', 'Baker LLC', '486 Walnut Rd', 'Kansas City', 'USA', 'wholesale', 20000.00),
('Donna Nelson', 'dnelson@email.com', '+1-555-0134', NULL, '597 Chestnut Dr', 'Mesa', 'USA', 'retail', 2600.00),
('Jason Carter', 'jcarter@email.com', '+1-555-0135', 'Carter Tech', '618 Sycamore Ln', 'Atlanta', 'USA', 'corporate', 16000.00),
('Carol Mitchell', 'cmitchell@email.com', '+1-555-0136', NULL, '729 Magnolia Way', 'Omaha', 'USA', 'retail', 4300.00),
('Ryan Perez', 'rperez@business.com', '+1-555-0137', 'Perez Corp', '831 Dogwood St', 'Miami', 'USA', 'wholesale', 23000.00),
('Michelle Roberts', 'mroberts@email.com', '+1-555-0138', NULL, '942 Redwood Ave', 'Cleveland', 'USA', 'retail', 3100.00),
('Gary Turner', 'gturner@email.com', '+1-555-0139', 'Turner Industries', '153 Sequoia Rd', 'Minneapolis', 'USA', 'corporate', 15000.00),
('Laura Phillips', 'lphillips@email.com', '+1-555-0140', NULL, '264 Cypress Dr', 'Tulsa', 'USA', 'retail', 3700.00),
('Eric Campbell', 'ecampbell@company.com', '+1-555-0141', 'Campbell Group', '375 Fir Ln', 'Arlington', 'USA', 'wholesale', 17000.00),
('Sharon Parker', 'sparker@email.com', '+1-555-0142', NULL, '486 Cedar Way', 'New Orleans', 'USA', 'retail', 2800.00),
('Jeffrey Evans', 'jevans@email.com', '+1-555-0143', 'Evans Solutions', '597 Pine St', 'Wichita', 'USA', 'corporate', 12000.00),
('Cynthia Edwards', 'cedwards@email.com', '+1-555-0144', NULL, '618 Oak Ave', 'Bakersfield', 'USA', 'retail', 4000.00),
('Frank Collins', 'fcollins@business.com', '+1-555-0145', 'Collins LLC', '729 Maple Rd', 'Tampa', 'USA', 'wholesale', 21000.00),
('Kathleen Stewart', 'kstewart@email.com', '+1-555-0146', NULL, '831 Elm Dr', 'Anaheim', 'USA', 'retail', 3500.00),
('Raymond Sanchez', 'rsanchez@email.com', '+1-555-0147', 'Sanchez Corp', '942 Birch Ln', 'Honolulu', 'USA', 'corporate', 14000.00),
('Deborah Morris', 'dmorris@email.com', '+1-555-0148', NULL, '153 Spruce Way', 'Aurora', 'USA', 'retail', 2900.00),
('Gregory Rogers', 'grogers@company.com', '+1-555-0149', 'Rogers Industries', '264 Ash St', 'Santa Ana', 'USA', 'wholesale', 19000.00),
('Ruth Reed', 'rreed@email.com', '+1-555-0150', NULL, '375 Willow Ave', 'Corpus Christi', 'USA', 'retail', 3300.00);

INSERT INTO invoice (invoice_number, customer_id, invoice_date, due_date, subtotal, tax_amount, discount_amount, total_amount, status, payment_method) VALUES
('INV-2025-001', 1, '2025-09-15 10:30:00', '2025-10-15 10:30:00', 5299.95, 424.00, 0, 5723.95, 'paid', 'bank_transfer'),
('INV-2025-002', 5, '2025-09-16 14:20:00', '2025-10-16 14:20:00', 2899.96, 232.00, 100.00, 3031.96, 'paid', 'credit_card'),
('INV-2025-003', 8, '2025-09-18 09:15:00', '2025-10-18 09:15:00', 1049.94, 84.00, 0, 1133.94, 'paid', 'cash'),
('INV-2025-004', 12, '2025-09-20 11:45:00', '2025-10-20 11:45:00', 799.96, 64.00, 50.00, 813.96, 'paid', 'credit_card'),
('INV-2025-005', 3, '2025-09-22 16:30:00', '2025-10-22 16:30:00', 12599.92, 1008.00, 500.00, 13107.92, 'paid', 'bank_transfer'),
('INV-2025-006', 15, '2025-09-25 10:00:00', '2025-10-25 10:00:00', 3499.95, 280.00, 150.00, 3629.95, 'paid', 'credit_card'),
('INV-2025-007', 20, '2025-09-26 13:30:00', '2025-10-26 13:30:00', 649.95, 52.00, 0, 701.95, 'paid', 'cash'),
('INV-2025-008', 7, '2025-09-27 15:45:00', '2025-10-27 15:45:00', 8999.94, 720.00, 300.00, 9419.94, 'paid', 'bank_transfer'),
('INV-2025-009', 25, '2025-09-28 09:20:00', '2025-10-28 09:20:00', 1899.95, 152.00, 0, 2051.95, 'paid', 'credit_card'),
('INV-2025-010', 30, '2025-09-29 14:10:00', '2025-10-29 14:10:00', 549.96, 44.00, 25.00, 568.96, 'paid', 'credit_card'),
('INV-2025-011', 2, '2025-10-01 10:15:00', '2025-10-31 10:15:00', 4299.96, 344.00, 200.00, 4443.96, 'paid', 'bank_transfer'),
('INV-2025-012', 10, '2025-10-02 11:30:00', '2025-11-01 11:30:00', 899.95, 72.00, 0, 971.95, 'pending', 'credit_card'),
('INV-2025-013', 18, '2025-10-03 16:00:00', '2025-11-02 16:00:00', 1599.94, 128.00, 75.00, 1652.94, 'pending', 'bank_transfer'),
('INV-2025-014', 22, '2025-10-05 09:45:00', '2025-11-04 09:45:00', 749.96, 60.00, 0, 809.96, 'pending', 'cash'),
('INV-2025-015', 9, '2025-10-06 13:20:00', '2025-11-05 13:20:00', 6799.93, 544.00, 250.00, 7093.93, 'paid', 'bank_transfer'),
('INV-2025-016', 35, '2025-10-08 10:30:00', '2025-11-07 10:30:00', 2299.95, 184.00, 100.00, 2383.95, 'pending', 'credit_card'),
('INV-2025-017', 40, '2025-10-09 14:50:00', '2025-11-08 14:50:00', 499.97, 40.00, 0, 539.97, 'pending', 'credit_card'),
('INV-2025-018', 14, '2025-10-10 11:15:00', '2025-11-09 11:15:00', 1249.94, 100.00, 50.00, 1299.94, 'paid', 'cash'),
('INV-2025-019', 28, '2025-10-12 15:30:00', '2025-11-11 15:30:00', 849.96, 68.00, 0, 917.96, 'pending', 'credit_card'),
('INV-2025-020', 6, '2025-10-13 09:00:00', '2025-11-12 09:00:00', 3899.94, 312.00, 150.00, 4061.94, 'paid', 'bank_transfer'),
('INV-2025-021', 45, '2025-10-15 12:45:00', '2025-11-14 12:45:00', 5599.92, 448.00, 200.00, 5847.92, 'pending', 'bank_transfer'),
('INV-2025-022', 11, '2025-10-16 10:20:00', '2025-11-15 10:20:00', 1099.95, 88.00, 0, 1187.95, 'pending', 'credit_card'),
('INV-2025-023', 33, '2025-10-18 14:00:00', '2025-11-17 14:00:00', 2499.96, 200.00, 100.00, 2599.96, 'paid', 'bank_transfer'),
('INV-2025-024', 17, '2025-10-19 16:30:00', '2025-11-18 16:30:00', 699.95, 56.00, 0, 755.95, 'pending', 'cash'),
('INV-2025-025', 50, '2025-10-20 11:00:00', '2025-11-19 11:00:00', 949.96, 76.00, 25.00, 1000.96, 'pending', 'credit_card'),
('INV-2025-026', 4, '2025-10-22 13:15:00', '2025-11-21 13:15:00', 7299.93, 584.00, 300.00, 7583.93, 'paid', 'bank_transfer'),
('INV-2025-027', 38, '2025-10-23 09:30:00', '2025-11-22 09:30:00', 1799.94, 144.00, 75.00, 1868.94, 'pending', 'credit_card'),
('INV-2025-028', 26, '2025-10-25 15:00:00', '2025-11-24 15:00:00', 599.97, 48.00, 0, 647.97, 'pending', 'cash'),
('INV-2025-029', 13, '2025-10-27 10:45:00', '2025-11-26 10:45:00', 4199.95, 336.00, 150.00, 4385.95, 'pending', 'bank_transfer'),
('INV-2025-030', 48, '2025-10-28 14:30:00', '2025-11-27 14:30:00', 1399.95, 112.00, 50.00, 1461.95, 'pending', 'credit_card');

INSERT INTO invoice_item (invoice_id, product_id, quantity, unit_price, discount_percent, line_total) VALUES
(1, 1, 3, 1299.99, 0, 3899.97),
(1, 11, 2, 399.99, 0, 799.98),
(1, 20, 2, 299.99, 0, 599.98),
(2, 4, 1, 2499.99, 0, 2499.99),
(2, 11, 1, 399.99, 0, 399.99),
(3, 6, 2, 129.99, 0, 259.98),
(3, 11, 2, 199.99, 0, 399.98),
(3, 14, 3, 129.99, 0, 389.97),
(4, 5, 10, 29.99, 0, 299.90),
(4, 7, 15, 19.99, 0, 299.85),
(4, 16, 5, 24.99, 0, 124.95),
(4, 26, 3, 24.99, 0, 74.97),
(5, 1, 6, 1299.99, 0, 7799.94),
(5, 2, 2, 1899.99, 0, 3799.98),
(5, 8, 10, 79.99, 0, 799.90),
(6, 21, 3, 599.99, 0, 1799.97),
(7, 33, 2, 349.99, 0, 699.98),
(7, 9, 3, 149.99, 0, 449.97),
(7, 22, 1, 45.99, 0, 45.99),
(7, 25, 2, 14.99, 0, 29.98),
(7, 27, 5, 9.99, 0, 49.95),
(7, 28, 4, 29.99, 0, 119.96),
(8, 2, 4, 1899.99, 0, 7599.96),
(8, 6, 5, 129.99, 0, 649.95),
(8, 20, 2, 299.99, 0, 599.98),
(8, 14, 1, 129.99, 0, 129.99),
(9, 29, 2, 149.99, 0, 299.98),
(9, 30, 1, 59.99, 0, 59.99),
(9, 3, 1, 999.99, 0, 999.99),
(9, 17, 5, 79.99, 0, 399.95),
(10, 31, 1, 69.99, 0, 69.99),
(10, 32, 2, 159.99, 0, 319.98),
(10, 33, 1, 99.99, 0, 99.99),
(10, 7, 3, 19.99, 0, 59.97),
(11, 1, 2, 1299.99, 0, 2599.98),
(11, 11, 3, 399.99, 0, 1199.97),
(11, 8, 5, 79.99, 0, 399.95),
(12, 14, 4, 129.99, 0, 519.96),
(12, 15, 3, 99.99, 0, 299.97),
(12, 7, 4, 19.99, 0, 79.96),
(13, 21, 2, 599.99, 0, 1199.98),
(13, 11, 1, 199.99, 0, 199.99),
(13, 12, 1, 199.99, 0, 199.99),
(14, 5, 15, 29.99, 0, 449.85),
(14, 25, 20, 14.99, 0, 299.80),
(15, 4, 2, 2499.99, 0, 4999.98),
(15, 34, 3, 399.99, 0, 1199.97),
(15, 6, 4, 129.99, 0, 519.96),
(16, 2, 1, 1899.99, 0, 1899.99),
(16, 11, 1, 199.99, 0, 199.99),
(16, 12, 1, 199.99, 0, 199.99),
(17, 35, 2, 19.99, 0, 39.98),
(17, 36, 10, 34.99, 0, 349.90),
(17, 16, 4, 24.99, 0, 99.96),
(18, 17, 8, 79.99, 0, 639.92),
(18, 18, 10, 49.99, 0, 499.90),
(18, 19, 8, 12.99, 0, 103.92),
(19, 29, 3, 149.99, 0, 449.97),
(19, 11, 1, 199.99, 0, 199.99),
(19, 12, 1, 199.99, 0, 199.99),
(20, 1, 2, 1299.99, 0, 2599.98),
(20, 20, 3, 299.99, 0, 899.97),
(20, 11, 1, 199.99, 0, 199.99),
(21, 4, 2, 2499.99, 0, 4999.98),
(21, 6, 3, 129.99, 0, 389.97),
(21, 12, 1, 199.99, 0, 199.99),
(22, 14, 5, 129.99, 0, 649.95),
(22, 15, 4, 99.99, 0, 399.96),
(22, 7, 2, 19.99, 0, 39.98),
(23, 1, 1, 1299.99, 0, 1299.99),
(23, 11, 2, 399.99, 0, 799.98),
(23, 11, 1, 199.99, 0, 199.99),
(24, 31, 5, 69.99, 0, 349.95),
(24, 33, 3, 99.99, 0, 299.97),
(24, 7, 2, 19.99, 0, 39.98),
(25, 37, 5, 89.99, 0, 449.95),
(25, 38, 2, 199.99, 0, 399.98),
(25, 16, 4, 24.99, 0, 99.96),
(26, 2, 3, 1899.99, 0, 5699.97),
(26, 11, 3, 399.99, 0, 1199.97),
(26, 11, 1, 199.99, 0, 199.99),
(27, 3, 1, 999.99, 0, 999.99),
(27, 11, 2, 199.99, 0, 399.98),
(27, 11, 1, 199.99, 0, 199.99),
(28, 24, 8, 24.99, 0, 199.92),
(28, 25, 20, 14.99, 0, 299.80),
(28, 26, 10, 9.99, 0, 99.90),
(29, 1, 2, 1299.99, 0, 2599.98),
(29, 21, 2, 599.99, 0, 1199.98),
(29, 11, 1, 199.99, 0, 199.99),
(30, 20, 3, 299.99, 0, 899.97),
(30, 8, 5, 79.99, 0, 399.95),
(30, 7, 5, 19.99, 0, 99.95);

INSERT INTO sale (customer_id, product_id, invoice_id, product_name, amount, quantity, sale_date, customer_name, category, payment_status, sales_channel) VALUES
(1, 1, 1, 'Laptop Pro 15"', 3899.97, 3, '2025-09-15 10:30:00', 'John Smith', 'Computers', 'completed', 'online'),
(1, 11, 1, 'Monitor 27" 4K', 799.98, 2, '2025-09-15 10:30:00', 'John Smith', 'Video', 'completed', 'online'),
(5, 4, 2, 'Gaming Desktop', 2499.99, 1, '2025-09-16 14:20:00', 'David Wilson', 'Gaming', 'completed', 'in_store'),
(8, 6, 3, 'Mechanical Keyboard RGB', 259.98, 2, '2025-09-18 09:15:00', 'Jennifer Taylor', 'Peripherals', 'completed', 'online'),
(12, 5, 4, 'Wireless Mouse Pro', 299.90, 10, '2025-09-20 11:45:00', 'Mary Harris', 'Peripherals', 'completed', 'online'),
(3, 1, 5, 'Laptop Pro 15"', 7799.94, 6, '2025-09-22 16:30:00', 'Michael Brown', 'Computers', 'completed', 'in_store'),
(15, 21, 6, 'Standing Desk Adjustable', 1799.97, 3, '2025-09-25 10:00:00', 'Matthew Garcia', 'Furniture', 'completed', 'online'),
(20, 22, 7, 'Desk Lamp LED', 45.99, 1, '2025-09-26 13:30:00', 'Susan Lewis', 'Furniture', 'completed', 'in_store'),
(7, 2, 8, 'Desktop Workstation', 7599.96, 4, '2025-09-27 15:45:00', 'James Anderson', 'Computers', 'completed', 'online'),
(25, 29, 9, 'Productivity Suite License', 299.98, 2, '2025-09-28 09:20:00', 'Kevin Young', 'Software', 'completed', 'online'),
(30, 31, 10, 'Gaming Mouse RGB', 69.99, 1, '2025-09-29 14:10:00', 'Helen Scott', 'Gaming', 'completed', 'online'),
(2, 1, 11, 'Laptop Pro 15"', 2599.98, 2, '2025-10-01 10:15:00', 'Sarah Johnson', 'Computers', 'completed', 'online'),
(10, 14, 12, 'External SSD 1TB', 519.96, 4, '2025-10-02 11:30:00', 'Linda Jackson', 'Storage', 'pending', 'online'),
(18, 21, 13, 'Standing Desk Adjustable', 1199.98, 2, '2025-10-03 16:00:00', 'Barbara Clark', 'Furniture', 'pending', 'in_store'),
(22, 5, 14, 'Wireless Mouse Pro', 449.85, 15, '2025-10-05 09:45:00', 'Karen Walker', 'Peripherals', 'pending', 'online'),
(9, 4, 15, 'Gaming Desktop', 4999.98, 2, '2025-10-06 13:20:00', 'Robert Thomas', 'Gaming', 'completed', 'online'),
(35, 2, 16, 'Desktop Workstation', 1899.99, 1, '2025-10-08 10:30:00', 'Jason Carter', 'Computers', 'pending', 'in_store'),
(40, 35, 17, 'Phone Case Universal', 39.98, 2, '2025-10-09 14:50:00', 'Laura Phillips', 'Mobile', 'pending', 'online'),
(14, 17, 18, 'WiFi Router AC', 639.92, 8, '2025-10-10 11:15:00', 'Patricia Thompson', 'Networking', 'completed', 'online'),
(28, 29, 19, 'Productivity Suite License', 449.97, 3, '2025-10-12 15:30:00', 'Betty Wright', 'Software', 'pending', 'online'),
(6, 1, 20, 'Laptop Pro 15"', 2599.98, 2, '2025-10-13 09:00:00', 'Jessica Martinez', 'Computers', 'completed', 'online'),
(45, 4, 21, 'Gaming Desktop', 4999.98, 2, '2025-10-15 12:45:00', 'Frank Collins', 'Gaming', 'pending', 'in_store'),
(11, 14, 22, 'External SSD 1TB', 649.95, 5, '2025-10-16 10:20:00', 'Christopher White', 'Storage', 'pending', 'online'),
(33, 1, 23, 'Laptop Pro 15"', 1299.99, 1, '2025-10-18 14:00:00', 'Ronald Baker', 'Computers', 'completed', 'online'),
(17, 31, 24, 'Gaming Mouse RGB', 349.95, 5, '2025-10-19 16:30:00', 'Anthony Robinson', 'Gaming', 'pending', 'online'),
(50, 37, 25, 'Security Camera WiFi', 449.95, 5, '2025-10-20 11:00:00', 'Ruth Reed', 'Security', 'pending', 'online'),
(4, 2, 26, 'Desktop Workstation', 5699.97, 3, '2025-10-22 13:15:00', 'Emily Davis', 'Computers', 'completed', 'online'),
(38, 3, 27, 'Laptop Ultra 13"', 999.99, 1, '2025-10-23 09:30:00', 'Michelle Roberts', 'Computers', 'pending', 'in_store'),
(26, 24, 28, 'Notebook Set Premium', 199.92, 8, '2025-10-25 15:00:00', 'Lisa Hernandez', 'Stationery', 'pending', 'online'),
(13, 1, 29, 'Laptop Pro 15"', 2599.98, 2, '2025-10-27 10:45:00', 'Daniel Martin', 'Computers', 'pending', 'online'),
(48, 20, 30, 'Office Chair Executive', 899.97, 3, '2025-10-28 14:30:00', 'Deborah Morris', 'Furniture', 'pending', 'in_store'),
(16, 11, NULL, 'Monitor 27" 4K', 399.99, 1, '2025-09-17 10:00:00', 'Elizabeth Martinez', 'Video', 'completed', 'online'),
(24, 8, NULL, 'Webcam HD Pro', 79.99, 1, '2025-09-19 14:30:00', 'Nancy Allen', 'Peripherals', 'completed', 'online'),
(19, 9, NULL, 'Wireless Headset', 149.99, 1, '2025-09-21 11:20:00', 'Mark Rodriguez', 'Audio', 'completed', 'in_store'),
(27, 10, NULL, 'USB Hub 7-Port', 39.99, 1, '2025-09-24 16:45:00', 'Brian King', 'Accessories', 'completed', 'online'),
(32, 13, NULL, 'Dual Monitor Stand', 89.99, 1, '2025-09-30 09:30:00', 'Sandra Adams', 'Accessories', 'completed', 'online'),
(36, 16, NULL, 'USB Flash Drive 128GB', 24.99, 1, '2025-10-04 13:15:00', 'Carol Mitchell', 'Storage', 'completed', 'online'),
(41, 19, NULL, 'Ethernet Cable 5m', 12.99, 1, '2025-10-07 10:45:00', 'Eric Campbell', 'Networking', 'completed', 'online'),
(44, 23, NULL, 'Monitor Riser', 39.99, 1, '2025-10-11 15:20:00', 'Cynthia Edwards', 'Furniture', 'completed', 'in_store'),
(46, 27, NULL, 'Desk Organizer', 29.99, 1, '2025-10-14 11:00:00', 'Kathleen Stewart', 'Stationery', 'completed', 'online'),
(47, 30, NULL, 'Antivirus Pro 1-Year', 59.99, 1, '2025-10-17 14:40:00', 'Raymond Sanchez', 'Security', 'completed', 'online'),
(49, 34, NULL, 'Tablet 10" WiFi', 399.99, 1, '2025-10-21 10:30:00', 'Gregory Rogers', 'Mobile', 'completed', 'online'),
(23, 36, NULL, 'Wireless Charger Pad', 34.99, 1, '2025-10-24 16:15:00', 'Steven Hall', 'Mobile', 'completed', 'online'),
(29, 38, NULL, 'Smart Door Lock', 199.99, 1, '2025-10-26 09:50:00', 'George Lopez', 'Security', 'completed', 'in_store'),
(37, 32, NULL, 'Gaming Keyboard Mechanical', 159.99, 1, '2025-10-29 13:25:00', 'Ryan Perez', 'Gaming', 'completed', 'online'),
(39, 15, NULL, 'External HDD 4TB', 99.99, 1, '2025-10-30 10:10:00', 'Gary Turner', 'Storage', 'pending', 'online'),
(42, 18, NULL, 'Network Switch 8-Port', 49.99, 1, '2025-10-30 15:30:00', 'Jeffrey Evans', 'Networking', 'pending', 'online'),
(43, 26, NULL, 'Sticky Notes Combo', 9.99, 1, '2025-10-30 11:45:00', 'Sharon Parker', 'Stationery', 'completed', 'online'),
(21, 12, NULL, 'Monitor 24" FHD', 199.99, 1, '2025-10-30 14:20:00', 'Paul Lee', 'Video', 'completed', 'online'),
(34, 25, NULL, 'Pen Pack Gel 12pc', 14.99, 1, '2025-10-30 16:00:00', 'Donna Nelson', 'Stationery', 'completed', 'in_store'),
(31, 28, NULL, 'Photo Editor Pro', 299.99, 1, '2025-10-30 12:30:00', 'Edward Green', 'Software', 'pending', 'online');

CREATE OR REPLACE VIEW sales_summary AS
SELECT
    DATE_TRUNC('month', sale_date) as month,
    COUNT(*) as total_sales,
    SUM(amount) as total_revenue,
    SUM(quantity) as total_items_sold,
    AVG(amount) as avg_sale_amount
FROM sale
GROUP BY DATE_TRUNC('month', sale_date)
ORDER BY month DESC;

CREATE OR REPLACE VIEW customer_purchase_summary AS
SELECT
    c.id,
    c.customer_name,
    c.email,
    COUNT(DISTINCT s.id) as total_purchases,
    SUM(s.amount) as total_spent,
    AVG(s.amount) as avg_purchase_amount,
    MAX(s.sale_date) as last_purchase_date
FROM customer c
LEFT JOIN sale s ON c.id = s.customer_id
GROUP BY c.id, c.customer_name, c.email
ORDER BY total_spent DESC NULLS LAST;

CREATE OR REPLACE VIEW product_performance AS
SELECT
    p.id,
    p.product_name,
    c.category_name,
    COUNT(DISTINCT s.id) as times_sold,
    SUM(s.quantity) as total_quantity_sold,
    SUM(s.amount) as total_revenue,
    p.stock_quantity as current_stock
FROM product p
LEFT JOIN category c ON p.category_id = c.id
LEFT JOIN sale s ON p.id = s.product_id
GROUP BY p.id, p.product_name, c.category_name, p.stock_quantity
ORDER BY total_revenue DESC NULLS LAST;

INSERT INTO roles (name, description) VALUES
('admin', 'Full system administrator with all permissions'),
('analyst', 'Data analyst with read access to data and AI tools'),
('viewer', 'Read-only access to reports and basic data'),
('developer', 'Developer with MCP tool management capabilities'),
('manager', 'Manager with full data access and limited admin functions');

INSERT INTO permissions (code, description, category) VALUES
('ai.use', 'Use AI models for chat and analysis', 'AI'),
('ai.model.gpt-4o.use', 'Use GPT-4o model specifically', 'AI'),
('ai.model.gpt-4o-mini.use', 'Use GPT-4o-mini model specifically', 'AI'),
('ai.model.gpt-3.5-turbo.use', 'Use GPT-3.5-turbo model specifically', 'AI'),
('ai.tokens.view', 'View token usage statistics', 'AI'),
('ai.tokens.manage', 'Manage token limits and usage', 'AI'),

('mcp.sales.view', 'View sales data through MCP tools', 'MCP'),
('mcp.sales.edit', 'Edit sales data through MCP tools', 'MCP'),
('mcp.customers.view', 'View customer data through MCP tools', 'MCP'),
('mcp.customers.edit', 'Edit customer data through MCP tools', 'MCP'),
('mcp.products.view', 'View product data through MCP tools', 'MCP'),
('mcp.products.edit', 'Edit product data through MCP tools', 'MCP'),
('mcp.invoices.view', 'View invoice data through MCP tools', 'MCP'),
('mcp.invoices.edit', 'Edit invoice data through MCP tools', 'MCP'),
('mcp.analytics.view', 'View analytics and reports through MCP tools', 'MCP'),
('mcp.charts.create', 'Create charts and visualizations', 'MCP'),
('mcp.tools.manage', 'Manage MCP tool registration and configuration', 'MCP'),

('system.users.view', 'View user information', 'System'),
('system.users.manage', 'Manage user accounts and permissions', 'System'),
('system.health.view', 'View system health and status', 'System'),
('system.logs.view', 'View system logs', 'System');

INSERT INTO role_permissions (role_id, permission_id) VALUES
(1, 1), (1, 2), (1, 3), (1, 4), (1, 5), (1, 6),
(1, 7), (1, 8), (1, 9), (1, 10), (1, 11), (1, 12), (1, 13), (1, 14), (1, 15), (1, 16), (1, 17), -- MCP permissions
(1, 18), (1, 19), (1, 20), (1, 21),

(2, 1), (2, 2), (2, 3), (2, 4), (2, 5),
(2, 7), (2, 9), (2, 11), (2, 13), (2, 15), (2, 16),
(2, 20), 

(3, 1), (3, 4), (3, 5),
(3, 7), (3, 9), (3, 11), (3, 13), (3, 15),
(3, 20),

(4, 1), (4, 2), (4, 3), (4, 4),
(4, 7), (4, 9), (4, 11), (4, 13), (4, 15), (4, 17),
(4, 18), (4, 20),

(5, 1), (5, 2), (5, 3), (5, 4), (5, 5), (5, 6),
(5, 7), (5, 8), (5, 9), (5, 10), (5, 11), (5, 12), (5, 13), (5, 14), (5, 15), (5, 16),
(5, 18), (5, 20), (5, 21);

INSERT INTO tool_permissions (tool_name, permission_code) VALUES
('sales_analysis', 'mcp.sales.view'),
('sales_report', 'mcp.sales.view'),
('sales_create', 'mcp.sales.edit'),
('sales_update', 'mcp.sales.edit'),
('customer_list', 'mcp.customers.view'),
('customer_details', 'mcp.customers.view'),
('customer_create', 'mcp.customers.edit'),
('customer_update', 'mcp.customers.edit'),
('product_list', 'mcp.products.view'),
('product_details', 'mcp.products.view'),
('product_create', 'mcp.products.edit'),
('product_update', 'mcp.products.edit'),
('invoice_list', 'mcp.invoices.view'),
('invoice_details', 'mcp.invoices.view'),
('invoice_create', 'mcp.invoices.edit'),
('invoice_update', 'mcp.invoices.edit'),
('analytics_dashboard', 'mcp.analytics.view'),
('create_chart', 'mcp.charts.create'),
('export_data', 'mcp.analytics.view');
