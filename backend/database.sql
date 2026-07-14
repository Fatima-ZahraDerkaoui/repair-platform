CREATE TABLE client (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    telephone VARCHAR(20) NOT NULL,
    email VARCHAR(100),
    adresse TEXT,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE utilisateur (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(30) NOT NULL,
    telephone VARCHAR(20)
);

CREATE TABLE stock (
    id SERIAL PRIMARY KEY,
    nom_piece VARCHAR(150) NOT NULL,
    reference VARCHAR(100),
    categorie VARCHAR(100),
    quantite INT NOT NULL,
    seuil_min INT DEFAULT 5,
    prix_unitaire DECIMAL(10,2),
    fournisseur VARCHAR(150),
    date_ajout TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE reparation (

    id SERIAL PRIMARY KEY,

    client_id INT REFERENCES client(id),

    receptionniste_id INT REFERENCES utilisateur(id),

    date_reception TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    type_materiel VARCHAR(50),

    systeme_exploitation VARCHAR(50),

    version_office VARCHAR(50),

    origine_probleme VARCHAR(50),

    probleme TEXT,

    remarques TEXT,

    urgent BOOLEAN DEFAULT FALSE,

    resolu BOOLEAN DEFAULT FALSE,

    statut VARCHAR(30) DEFAULT 'En attente',

    qr_code VARCHAR(255),

    texte_ocr TEXT,

    delai_estime INT,

    cout_estime DECIMAL(10,2),

    cout_reel DECIMAL(10,2),

    date_fin TIMESTAMP
);

CREATE TABLE reparation_piece (

    id SERIAL PRIMARY KEY,

    reparation_id INT REFERENCES reparation(id),

    piece_id INT REFERENCES stock(id),

    quantite INT NOT NULL,

    prix_utilise DECIMAL(10,2)

);

CREATE TABLE historique_statut (

    id SERIAL PRIMARY KEY,

    reparation_id INT REFERENCES reparation(id),

    ancien_statut VARCHAR(30),

    nouveau_statut VARCHAR(30),

    utilisateur_id INT REFERENCES utilisateur(id),

    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

CREATE TABLE notification (

    id SERIAL PRIMARY KEY,

    reparation_id INT REFERENCES reparation(id),

    client_id INT REFERENCES client(id),

    type_notification VARCHAR(30),

    message TEXT,

    date_envoi TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    statut VARCHAR(30)

);

CREATE TABLE prediction_delai (

    id SERIAL PRIMARY KEY,

    reparation_id INT REFERENCES reparation(id),

    modele_ia VARCHAR(100),

    delai_predit INT,

    precision_modele DECIMAL(5,2),

    date_prediction TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);

CREATE TABLE prediction_cout (

    id SERIAL PRIMARY KEY,

    reparation_id INT REFERENCES reparation(id),

    modele_ia VARCHAR(100),

    cout_predit DECIMAL(10,2),

    date_prediction TIMESTAMP DEFAULT CURRENT_TIMESTAMP

);