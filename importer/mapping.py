"""Column-to-Pipedrive field mapping for the importer."""

FIELD_MAPPING = {
    "Affaire - Titre de l'affaire - CD": {
        "entity": "deal",
        "pipedrive_field_name": "Titre de l'affaire",
    },
    "Affaire Étiquette - CD": {
        "entity": "deal",
        "pipedrive_field_name": "Étiquette d'affaire",
    },
    "Affaire Etape - CD": {
        "entity": "deal",
        "pipedrive_field_name": "Étape (Pipeline)",
    },
    "Affaire Téléphone 1 - CP": {
        "entity": "deal",
        "pipedrive_field_name": "Téléphone 1",
    },
    "Affaire Responsable 1 - CP": {
        "entity": "deal",
        "pipedrive_field_name": "Responsable 1",
    },
    "Affaire - Fonction responsable 1 - CP": {
        "entity": "deal",
        "pipedrive_field_name": "Fonction Responsable 1",
    },
    "Affaire - Responsable 2 - CP": {
        "entity": "deal",
        "pipedrive_field_name": "Responsable 2",
    },
    "Affaire - Fonction responsable 2 - CP": {
        "entity": "deal",
        "pipedrive_field_name": "Fonction Responsable 2",
    },
    "Organisation - Propriétaire – utilisateur - CD": {
        "entity": "organization",
        "pipedrive_field_name": "Le propriétaire de l'organisation",
    },
    "Organisation - CD": {
        "entity": "organization",
        "pipedrive_field_name": "Nom de l'organisation",
    },
    "Organisation - Adresse complète - CD": {
        "entity": "organization",
        "pipedrive_field_name": "Adresse",
    },
    "Organisation - Rue - CD": {
        "entity": "organization",
        "pipedrive_field_name": "Rue",
    },
    "Organisation - Code postal - CD": {
        "entity": "organization",
        "pipedrive_field_name": "Code postal",
    },
    "Organisation - Ville - CD": {
        "entity": "organization",
        "pipedrive_field_name": "Ville",
    },
    "Organisation - Téléphone 1 - CP": {
        "entity": "organization",
        "pipedrive_field_name": "Téléphone 1",
    },
    "Organisation - Responsable 1 - CP": {
        "entity": "organization",
        "pipedrive_field_name": "Responsable 1",
    },
    "Organisation - Fonction responsable 1 - CP": {
        "entity": "organization",
        "pipedrive_field_name": "Fonction responsable 1",
    },
    "Organisation - Responsable 2 - CP": {
        "entity": "organization",
        "pipedrive_field_name": "Responsable 2",
    },
    "Organisation - Fonction responsable 2 - CP": {
        "entity": "organization",
        "pipedrive_field_name": "Fonction responsable 2",
    },
    "Organisation - Responsable 3 - CP": {
        "entity": "organization",
        "pipedrive_field_name": "Responsable 3",
    },
    "Organisation - Fonction responsable 3 - CP": {
        "entity": "organization",
        "pipedrive_field_name": "Fonction responsable 3",
    },
    "Organisation - Responsable 4 - CP": {
        "entity": "organization",
        "pipedrive_field_name": "Responsable 4",
    },
    "Organisation - Fonction responsable 4 - CP": {
        "entity": "organization",
        "pipedrive_field_name": "Fonction responsable 4",
    },
    "Organisation - url inscription Local - CP": {
        "entity": "organization",
        "pipedrive_field_name": "url local.ch",
    },
    "Organisation - Secteur d'activité - CP": {
        "entity": "organization",
        "pipedrive_field_name": "Secteur d'activité",
    },
    "Organisation - Téléphone 2 - CP": {
        "entity": "organization",
        "pipedrive_field_name": "Téléphone 2",
    },
    "Organisation - Téléphone 3 - CP": {
        "entity": "organization",
        "pipedrive_field_name": "Téléphone 3",
    },
    "Organisation - Téléphone 4 - CP": {
        "entity": "organization",
        "pipedrive_field_name": "Téléphone 4",
    },
    "Organisation - email - email société - CP": {
        "entity": "organization",
        "pipedrive_field_name": "Email société",
    },
    "Organisation - website - CP": {
        "entity": "organization",
        "pipedrive_field_name": "Site Web",
    },
    "Organisation - Site Mywebsite - CP": {
        "entity": "organization",
        "pipedrive_field_name": "Site Mywebsite",
    },
    "Organisation - Copyright du site - CP": {
        "entity": "organization",
        "pipedrive_field_name": "Copyright du site",
    },
    "Organisation - Nombre de photos - CP": {
        "entity": "organization",
        "pipedrive_field_name": "Photos sur Local.ch",
    },
    "Organisation - Nombre d'avis - CP": {
        "entity": "organization",
        "pipedrive_field_name": "Nombre d'avis",
    },
    "Organisation - Zip - CP": {
        "entity": "organization",
        "pipedrive_field_name": "Annuaire ZIP",
    },
    "Organisation - has_social_media - CP": {
        "entity": "organization",
        "pipedrive_field_name": "Comptes sociaux",
    },
    "Organisation - facebook_url - CP": {
        "entity": "organization",
        "pipedrive_field_name": "facebook_url",
    },
    "Organisation - instagram_url - CP": {
        "entity": "organization",
        "pipedrive_field_name": "instagram_url",
    },
    "Organisation - linkedin_url - CP": {
        "entity": "organization",
        "pipedrive_field_name": "linkedin_url",
    },
    "Organisation - twitter_url - CP": {
        "entity": "organization",
        "pipedrive_field_name": "twitter_url",
    },
    "Organisation - youtube_url - CP": {
        "entity": "organization",
        "pipedrive_field_name": "Youtube_url",
    },
    "Personne - email - CD": {
        "entity": "person",
        "pipedrive_field_name": "Adresse e-mail (Travail)",
    },
    "Personne - Responsable 1_CD": {
        "entity": "person",
        "pipedrive_field_name": "Nom complet de la personne",
    },
    "Personne - Téléphone 1 - CD": {
        "entity": "person",
        "pipedrive_field_name": "Téléphone (Travail)",
    },
    "Personne - Téléphone 2 - CP": {
        "entity": "person",
        "pipedrive_field_name": "Téléphone 2",
    },
    "Personne - Responsable 1 - CP": {
        "entity": "person",
        "pipedrive_field_name": "Responsable 1",
    },
    "Personne - Fonction responsable 1 - CP": {
        "entity": "person",
        "pipedrive_field_name": "Fonction responsable 1",
    },
    "Personne - Responsable 2 - CP": {
        "entity": "person",
        "pipedrive_field_name": "Responsable 2",
    },
    "Personne - Fonction responsable 2 - CP": {
        "entity": "person",
        "pipedrive_field_name": "Fonction responsable 2",
    },
    "Personne - Responsable 3 - CP": {
        "entity": "person",
        "pipedrive_field_name": "Responsable 3",
    },
    "Personne - Fonction responsable 3 - CP": {
        "entity": "person",
        "pipedrive_field_name": "Fonction responsable 3",
    },
    "Personne - Responsable 4 - CP": {
        "entity": "person",
        "pipedrive_field_name": "Responsable 4",
    },
    "Personne - Fonction responsable 4 - CP": {
        "entity": "person",
        "pipedrive_field_name": "Fonction Responsable 4",
    },
}


STANDARD_FIELD_ALIASES = {
    "deal": {
        "Titre de l'affaire": "title",
        "Étiquette d'affaire": "label",
        "Étape (Pipeline)": "stage_id",
    },
    "organization": {
        "Le propriétaire de l'organisation": "owner_id",
        "Nom de l'organisation": "name",
        "Adresse": "address",
        "Rue": "address_route",
        "Code postal": "address_postal_code",
        "Ville": "address_locality",
    },
    "person": {
        "Nom complet de la personne": "name",
        "Adresse e-mail (Travail)": "email",
        "Téléphone (Travail)": "phone",
    },
}
