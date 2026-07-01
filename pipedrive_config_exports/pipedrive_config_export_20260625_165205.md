# Pipedrive Configuration Export

Exported at: `2026-06-25T16:52:05`
Base URL: `https://api.pipedrive.com/v1`

This file summarizes fields and account configuration needed to recreate custom setup in another Pipedrive environment.

## Fields

### Deal Fields

Endpoint: `dealFields`
Total fields: `55`
Likely custom fields: `7`

| Custom | Name | Key | Type | Options |
|---|---|---|---|---|
| no | ID | `id` | int |  |
| no | Title | `title` | varchar |  |
| no | Creator | `creator_user_id` | user |  |
| no | Owner | `user_id` | user |  |
| no | Value | `value` | monetary |  |
| no | Currency | `currency` | varchar |  |
| no | Weighted value | `weighted_value` | monetary |  |
| no | Currency of Weighted value | `weighted_value_currency` | varchar |  |
| no | Probability | `probability` | int |  |
| no | Organization | `org_id` | org |  |
| no | Pipeline | `pipeline` | double |  |
| no | Contact person | `person_id` | people |  |
| no | Stage | `stage_id` | stage |  |
| no | Status | `status` | status | Open, Lost, Won, Deleted |
| no | Deal created | `add_time` | date |  |
| no | Update time | `update_time` | date |  |
| no | Last stage change | `stage_change_time` | date |  |
| no | Next activity date | `next_activity_date` | date |  |
| no | Last activity date | `last_activity_date` | date |  |
| no | Won time | `won_time` | date |  |
| no | Last email received | `last_incoming_mail_time` | date |  |
| no | Last email sent | `last_outgoing_mail_time` | date |  |
| no | Lost time | `lost_time` | date |  |
| no | Deal closed on | `close_time` | date |  |
| no | Lost reason | `lost_reason` | varchar_options | Situation financière de l'entreprise, Manque de budget, A choisi un concurrent, Ne croit pas à Internet, Trop cher, Pas le temps / c'est trop tôt, Pas besoin de nouveaux clients / trop de boulot / tout va bien, Projets plus prioritaires, Raisons personnelles / en train de céder la sté, Entreprise trop petite, Nouveau Web offert par un fournisseur, Content de Localsearch, Raccroche au nez, Non décideurs car font partie d'un groupe, Bientôt en retraite sans repreneur, Prospect risqué (peu fiable / fragile), Impossible à joindre, "Pas intéressé" par retour de mail, sans justification, "Pas intéressé" par tél / en live, sans justification, En faillite, Vient de resigner avec Localsearch, Trop éloigné |
| no | Visible to | `visible_to` | visible_to | Item owner, All users |
| no | Total activities | `activities_count` | int |  |
| no | Done activities | `done_activities_count` | int |  |
| no | Activities to do | `undone_activities_count` | int |  |
| no | Email messages count | `email_messages_count` | int |  |
| no | Expected close date | `expected_close_date` | date |  |
| no | Product quantity | `product_quantity` | double |  |
| no | Product amount | `product_amount` | double |  |
| no | Label | `label` | set | PAS INTERESSÉ, TOP, TOP 2, TOP3, TOP 4, 10 Juin 2026, Import juin 2026, abc |
| no | Product name | `product_name` | varchar |  |
| no | MRR | `mrr` | monetary |  |
| no | Currency of MRR | `mrr_currency` | varchar |  |
| no | ARR | `arr` | monetary |  |
| no | Currency of ARR | `arr_currency` | varchar |  |
| no | ACV | `acv` | monetary |  |
| no | Currency of ACV | `acv_currency` | varchar |  |
| no | Source origin | `origin` | enum | Manually created, Import, API, Automation, Marketplace, Prospector, Lead suggestions, Web Forms, Chatbot, Live Chat, Web Visitors, Campaigns, Messaging inbox |
| no | Source origin ID | `origin_id` | varchar |  |
| no | Source channel | `channel` | enum | Prospector, Lead Suggestions, Web forms, Chatbot, Live chat, Web visitors, Campaigns, Marketplace, Messaging Inbox |
| no | Source channel ID | `channel_id` | varchar |  |
| no | Archive status | `is_archived` | enum | Not archived, Archived |
| no | Archive time | `archive_time` | date |  |
| no | Sequence enrollment | `sequence_enrollment` | boolean |  |
| yes | Origine prospect | `51661aeaddce1b969b8447b190b95c5992cb53ab` | set | Telemarketing, Entrant, Emailing, Recommandation, Recherche architectes.ch, Tuyaux suite appel autre prospect, Listes locales d'enteprises / BNI |
| yes | Pipeline | `874b703f65974683b1474c4c218bc19219c4cbc2` | set | ARTUR, FREDERIC, VINCENT |
| yes | Responsable 1 | `87c86f302a86023205fb0ecb21079bd111cb485e` | varchar |  |
| yes | Téléphone 1 | `4d6e5da3478a03531d79a64a97eabda85b16fa2d` | phone |  |
| yes | Fonction Responsable  1 | `2c7224b096617e4e76d9b56bb492be60e31eda47` | varchar |  |
| yes | Fonction Responsable 2 | `dd6c182eef207dc2fa2a1a595f321ca24a986ef2` | varchar |  |
| yes | Responsable 2 | `145b7e4435528389016cc72b9f3d03308f758a62` | varchar |  |

### Organization Fields

Endpoint: `organizationFields`
Total fields: `118`
Likely custom fields: `56`

| Custom | Name | Key | Type | Options |
|---|---|---|---|---|
| no | ID | `id` | int |  |
| no | Name | `name` | varchar |  |
| no | Label | `label` | enum | ACHAT/VENTE, TEST |
| no | Owner | `owner_id` | user |  |
| no | People | `people_count` | double |  |
| no | Open deals | `open_deals_count` | double |  |
| no | Organization created | `add_time` | date |  |
| no | Update time | `update_time` | date |  |
| no | Visible to | `visible_to` | visible_to | Item owner, All users |
| no | Next activity date | `next_activity_date` | date |  |
| no | Last activity date | `last_activity_date` | date |  |
| no | Won deals | `won_deals_count` | int |  |
| no | Lost deals | `lost_deals_count` | int |  |
| no | Closed deals | `closed_deals_count` | int |  |
| no | Total activities | `activities_count` | int |  |
| no | Done activities | `done_activities_count` | int |  |
| no | Activities to do | `undone_activities_count` | int |  |
| no | Email messages count | `email_messages_count` | int |  |
| no | Profile picture | `picture_id` | picture |  |
| yes | Responsable 1 | `5f210f0f5a45e61183171acf37bc5ad7a088a1ab` | varchar |  |
| no | Address | `address` | address |  |
| no | Latitude of Address | `address_lat` | double |  |
| no | Longitude of Address | `address_long` | double |  |
| no | Apartment/suite no of Address | `address_subpremise` | varchar |  |
| no | House number of Address | `address_street_number` | varchar |  |
| no | Street/road name of Address | `address_route` | varchar |  |
| no | District/sublocality of Address | `address_sublocality` | varchar |  |
| no | City/town/village/locality of Address | `address_locality` | varchar |  |
| no | State/county of Address | `address_admin_area_level_1` | varchar |  |
| no | Region of Address | `address_admin_area_level_2` | varchar |  |
| no | Country of Address | `address_country` | varchar |  |
| no | ZIP/Postal code of Address | `address_postal_code` | varchar |  |
| no | Full/combined address of Address | `address_formatted_address` | varchar |  |
| yes | Rue | `1d3b59a8fbe73b031b7ee1b205d82ade81c79070` | varchar |  |
| no | Labels | `label_ids` | set | ACHAT/VENTE, TEST |
| yes | Téléphone société 1 | `d50649d6b2bae3a4de300102438257d8cf5bb8af` | varchar |  |
| yes | Téléphone 1 | `0b3be55de2cc3ab4426040bffdd33855a4b4b8fe` | phone |  |
| yes | Téléphone 2 | `ca526d5ca2fa78f83203318127fd22386574a53a` | phone |  |
| yes | Téléphone 3 | `44dba4a1b1e5f4551a41beb90812071e8c22363d` | phone |  |
| yes | Téléphone 4 | `8263bbc7011b05e2f208766f94efb5e845536773` | phone |  |
| no | Website | `website` | varchar |  |
| no | LinkedIn profile | `linkedin` | varchar |  |
| no | Industry | `industry` | enum | Accommodation services, Administrative and support services, Construction, Consumer services, Education, Entertainment providers, Farming, ranching, forestry, Financial services, Government administration, Holding companies, Hospitals and health care, Manufacturing, Oil, gas, and mining, Professional services, Real estate and equipment rental services, Retail, Technology, information and media, Transportation, logistics, supply chain and storage, Utilities, Wholesale |
| no | Annual revenue | `annual_revenue` | enum | 0, 1 - 10M USD, 10 - 100M USD, 100 - 1000M USD, 1 - 10B USD, 10+B USD |
| no | Number of employees | `employee_count` | int |  |
| yes | Remarque | `dea2abde178c1a028087191f8883baac7c5f6cde` | varchar |  |
| yes | Secteur d'activité | `e0444d280fbbb8d043c457bd69f6456c2da0963c` | varchar |  |
| yes | Téléphone société 2 | `30eab5faa0d44f0c1225d0714ab6a0ea07c5f2eb` | varchar |  |
| yes | Email société | `c6af70f2f2796779536ec43637060c86fcf97d85` | varchar |  |
| yes | Responsable 1 | `5172d2479924260c0ccec0beb87fc5d8c7368bc0` | people |  |
| yes | Titre Responsable 1 | `da246f498588676510662d5460093d5cd9f45372` | varchar |  |
| yes | Fixe Responsable 1 | `3dea31160db5b00450f2ad6d4026cfa995debe15` | phone |  |
| yes | Portable Responsable 1 | `2847ff4af990a9ff384560645b25999cf37df2aa` | phone |  |
| yes | Email Responsable 1 | `a062d0b6adebc1f969fbac6be6263489162da1a0` | varchar |  |
| yes | Responsable 2 | `8932f2a28c0b94dce30895897d98eb658cebd796` | people |  |
| yes | Titre Responsable 2 | `6f3ea8a34c25a72350cc8796fd33be264da3784d` | varchar |  |
| yes | Fixe Responsable 2 | `2511ac187f2a13be045257d339b11278df813bd9` | phone |  |
| yes | Portable Responsable 2 | `e95d376ba35876b1afc3790aba31ce2c8cd213da` | phone |  |
| yes | Email Responsable 2 | `507831985bb3adc2d15933b793b07c551138637e` | varchar |  |
| yes | Responsable 3 | `77d7b0ab3e863759814682059a3e8e03301941bd` | varchar |  |
| yes | Titre Responsable 3 | `1c27759b95fc58db7835581c1237161157d3bcaa` | varchar |  |
| yes | Fixe Responsable 3 | `073455f5fe897a267de7b0abbce6a76defc38a1d` | phone |  |
| yes | Portable Responsable 3 | `4d11119def2cc2521494f6052675ba3a3ffdb120` | phone |  |
| yes | Email Responsable 3 | `bb82d0666d9d599600c16fac5a92232cbd79edd8` | varchar |  |
| yes | Responsable 4 | `d4414dbdb450140f87ec55930b6983867314110f` | varchar |  |
| yes | Titre Responsable 4 | `00f2be787f2b67b7dbf728096966770bb01ec3d7` | varchar |  |
| yes | Site  Web | `0ca98ec33de92c76f581f653ceeead017caac93c` | varchar |  |
| yes | Code postal | `2018ed473ff6f8ca52a577718406d22593532274` | varchar |  |
| yes | Adresse 2 | `f148dbf6ca41b034b269938f225cb78674bff921` | address |  |
| no | Latitude of Adresse 2 | `f148dbf6ca41b034b269938f225cb78674bff921_lat` | double |  |
| no | Longitude of Adresse 2 | `f148dbf6ca41b034b269938f225cb78674bff921_long` | double |  |
| no | Apartment/suite no of Adresse 2 | `f148dbf6ca41b034b269938f225cb78674bff921_subpremise` | varchar |  |
| no | House number of Adresse 2 | `f148dbf6ca41b034b269938f225cb78674bff921_street_number` | varchar |  |
| no | Street/road name of Adresse 2 | `f148dbf6ca41b034b269938f225cb78674bff921_route` | varchar |  |
| no | District/sublocality of Adresse 2 | `f148dbf6ca41b034b269938f225cb78674bff921_sublocality` | varchar |  |
| no | City/town/village/locality of Adresse 2 | `f148dbf6ca41b034b269938f225cb78674bff921_locality` | varchar |  |
| no | State/county of Adresse 2 | `f148dbf6ca41b034b269938f225cb78674bff921_admin_area_level_1` | varchar |  |
| no | Region of Adresse 2 | `f148dbf6ca41b034b269938f225cb78674bff921_admin_area_level_2` | varchar |  |
| no | Country of Adresse 2 | `f148dbf6ca41b034b269938f225cb78674bff921_country` | varchar |  |
| no | ZIP/Postal code of Adresse 2 | `f148dbf6ca41b034b269938f225cb78674bff921_postal_code` | varchar |  |
| no | Full/combined address of Adresse 2 | `f148dbf6ca41b034b269938f225cb78674bff921_formatted_address` | varchar |  |
| yes | Ville | `2d238de82c039ac33a49c3772de3c4bc990af204` | address |  |
| no | Latitude of Ville | `2d238de82c039ac33a49c3772de3c4bc990af204_lat` | double |  |
| no | Longitude of Ville | `2d238de82c039ac33a49c3772de3c4bc990af204_long` | double |  |
| no | Apartment/suite no of Ville | `2d238de82c039ac33a49c3772de3c4bc990af204_subpremise` | varchar |  |
| no | House number of Ville | `2d238de82c039ac33a49c3772de3c4bc990af204_street_number` | varchar |  |
| no | Street/road name of Ville | `2d238de82c039ac33a49c3772de3c4bc990af204_route` | varchar |  |
| no | District/sublocality of Ville | `2d238de82c039ac33a49c3772de3c4bc990af204_sublocality` | varchar |  |
| no | City/town/village/locality of Ville | `2d238de82c039ac33a49c3772de3c4bc990af204_locality` | varchar |  |
| no | State/county of Ville | `2d238de82c039ac33a49c3772de3c4bc990af204_admin_area_level_1` | varchar |  |
| no | Region of Ville | `2d238de82c039ac33a49c3772de3c4bc990af204_admin_area_level_2` | varchar |  |
| no | Country of Ville | `2d238de82c039ac33a49c3772de3c4bc990af204_country` | varchar |  |
| no | ZIP/Postal code of Ville | `2d238de82c039ac33a49c3772de3c4bc990af204_postal_code` | varchar |  |
| no | Full/combined address of Ville | `2d238de82c039ac33a49c3772de3c4bc990af204_formatted_address` | varchar |  |
| yes | Site Web | `b17643504fb2fbf14d83fd04079cc7e9e9ef2707` | varchar |  |
| yes | Téléphone | `ac72de9f786afb7b088cccc8277f78171302adba` | phone |  |
| yes | Organization - Inscription Local | `7efc1d45d385b667c1f6a7c4f22e63cc31ff0e40` | varchar |  |
| yes | Téléphone société 3 | `f91d16624baabad11c386906cb8b55cf69ec31b5` | phone |  |
| yes | instagram_url | `acef2977093ecc60eed8bfffd3917c81f3571593` | varchar |  |
| yes | facebook_url | `1de7e8409e3abf5177db9d71e5da5911e65bd118` | varchar |  |
| yes | linkedin_url | `564883c3efc592a696c53cf264d649ede8137bf3` | varchar |  |
| yes | Responsable 2 | `1eef1ccb903f31f2c5579882444c190283a8a19c` | varchar |  |
| yes | Responsable 3 | `460703bacd539a4d9adc48319893d7fa33dce43f` | people |  |
| yes | url local.ch | `706e585f8f3a30e3e9c0d27b09780d69e54df8f7` | varchar |  |
| yes | Nombre d'avis | `2abcd3782298b77015d97a492139a289c33403e5` | double |  |
| yes | Site Mywebsite | `5ec86b366a9f9d3197e1f987c44e4da1ad14946f` | varchar |  |
| yes | Copyright du site | `029ab3600f069c4af1267e707b756a15a8938e58` | varchar |  |
| yes | Annuaire ZIP | `227e9e7a8ad00e15dbd23e5932d2a3d1005556f2` | varchar |  |
| yes | Comptes sociaux | `77247cc7cfa688f87d23078f0145e1e76c6699b6` | varchar |  |
| yes | Photos sur Local.ch | `fcea266cd0af8f888f4c08453fb49c7048dfc463` | double |  |
| yes | twitter_url | `3ef374f1991dd461a5f5c2dda4f6f4f7ac4cc9b4` | varchar |  |
| yes | YouTube_url | `58b6fe3c17a7f871b09b41f150883b8a17555f90` | varchar |  |
| yes | Nbre de personnes | `77b33aae27ff13655a080ef7c31b659941b808da` | varchar |  |
| yes | Fonction responsable 1 | `784ddb19c19d914bf00f5689d2e9ae447acc0d9c` | varchar |  |
| yes | Fonction responsable 2 | `ba60afb34cc9f368f196d10c0f848d60dd99b0b2` | varchar |  |
| yes | Responsable 4 | `9c7fa024e77db3dc7358d44aba84edd8c149b9da` | varchar |  |
| yes | Fonction responsable 3 | `63e71cd629e3054f2315ca77d39b6f733513a01d` | varchar |  |
| yes | Fonction responsable 4 | `ed0bec492f39bb34f69e36d6c4cbd61ef2606c1f` | varchar |  |

### Person Fields

Endpoint: `personFields`
Total fields: `49`
Likely custom fields: `11`

| Custom | Name | Key | Type | Options |
|---|---|---|---|---|
| no | ID | `id` | int |  |
| no | Name | `name` | varchar |  |
| no | Label | `label` | enum | Customer, Hot lead, Warm lead, Cold lead, FABRICE |
| no | Person created | `add_time` | date |  |
| no | Update time | `update_time` | date |  |
| no | Organization | `org_id` | org |  |
| no | Owner | `owner_id` | user |  |
| no | Open deals | `open_deals_count` | double |  |
| no | Visible to | `visible_to` | visible_to | Item owner, All users |
| no | Next activity date | `next_activity_date` | date |  |
| no | Last activity date | `last_activity_date` | date |  |
| no | Won deals | `won_deals_count` | int |  |
| no | Lost deals | `lost_deals_count` | int |  |
| no | Closed deals | `closed_deals_count` | int |  |
| no | Total activities | `activities_count` | int |  |
| no | Done activities | `done_activities_count` | int |  |
| no | Activities to do | `undone_activities_count` | int |  |
| no | Email messages count | `email_messages_count` | int |  |
| no | Profile picture | `picture_id` | picture |  |
| no | Last email received | `last_incoming_mail_time` | date |  |
| no | Last email sent | `last_outgoing_mail_time` | date |  |
| no | Phone | `phone` | phone |  |
| no | Email | `email` | varchar |  |
| no | First name | `first_name` | varchar |  |
| no | Last name | `last_name` | varchar |  |
| no | Labels | `label_ids` | set | Customer, Hot lead, Warm lead, Cold lead, FABRICE |
| yes | adresse | `fe8485b3ea39f297917beca59242700b918eaa2d` | address |  |
| no | Latitude of adresse | `fe8485b3ea39f297917beca59242700b918eaa2d_lat` | double |  |
| no | Longitude of adresse | `fe8485b3ea39f297917beca59242700b918eaa2d_long` | double |  |
| no | Apartment/suite no of adresse | `fe8485b3ea39f297917beca59242700b918eaa2d_subpremise` | varchar |  |
| no | House number of adresse | `fe8485b3ea39f297917beca59242700b918eaa2d_street_number` | varchar |  |
| no | Street/road name of adresse | `fe8485b3ea39f297917beca59242700b918eaa2d_route` | varchar |  |
| no | District/sublocality of adresse | `fe8485b3ea39f297917beca59242700b918eaa2d_sublocality` | varchar |  |
| no | City/town/village/locality of adresse | `fe8485b3ea39f297917beca59242700b918eaa2d_locality` | varchar |  |
| no | State/county of adresse | `fe8485b3ea39f297917beca59242700b918eaa2d_admin_area_level_1` | varchar |  |
| no | Region of adresse | `fe8485b3ea39f297917beca59242700b918eaa2d_admin_area_level_2` | varchar |  |
| no | Country of adresse | `fe8485b3ea39f297917beca59242700b918eaa2d_country` | varchar |  |
| no | ZIP/Postal code of adresse | `fe8485b3ea39f297917beca59242700b918eaa2d_postal_code` | varchar |  |
| no | Full/combined address of adresse | `fe8485b3ea39f297917beca59242700b918eaa2d_formatted_address` | varchar |  |
| yes | Responsable 1 | `0abfd5533fb911ea00996a5ebfabc74e223b3ea6` | varchar |  |
| yes | Fonction responsable 1 | `56c7ec84d7c4d68e734bf132b50a14754b5cc252` | varchar |  |
| yes | Fonction responsable 1 | `7ec0bcdcecc47d4ef91a357202f9a14283b65c8b` | varchar |  |
| yes | Téléphone 2 | `dc299e158baefb40ce3ecc0baf6b6caf9b40ffa4` | phone |  |
| yes | Responsable 2 | `05b3bec42221e5dda2f76764099b84b039ff42e6` | varchar |  |
| yes | Fonction responsable 2 | `385dd508224a1074e3f7b1e2a7d4b5dc12854879` | varchar |  |
| yes | Responsable 3 | `37a971a83f665d83e79c071434f49975bb5a47ac` | varchar |  |
| yes | Fonction responsable 3 | `4fe89b34d0d19906ec6fdd40c8b39d086dfce045` | varchar |  |
| yes | Responsable 4 | `5ff894111f9cc927250f5303fd000d580d0751bc` | varchar |  |
| yes | Fonction Responsable 4 | `68c11513f38ece7741ccebeef8e3ed8f3d3b5294` | varchar |  |

### Activity Fields

Endpoint: `activityFields`
Total fields: `35`
Likely custom fields: `0`

| Custom | Name | Key | Type | Options |
|---|---|---|---|---|
| no | ID | `id` | int |  |
| no | Subject | `subject` | varchar |  |
| no | Type | `type` | enum | APPEL 1, APPEL 2, APPEL 3, APPEL 4, APPEL 5, Appel secrétaire , 1er appel décideur, 2ème/Nième appel décideur , R1, R2 ou plus, Envoyer e-mail, RDV Suivi client, RDV Renouvellement Contrat, Task |
| no | Done | `done` | enum | To do, Done |
| no | Marked as done time | `marked_as_done_time` | date |  |
| no | Organization | `org_id` | org |  |
| no | Contact person | `person_id` | people |  |
| no | Deal | `deal_id` | deal |  |
| no | Due date | `due_date` | date |  |
| no | Due time | `due_time` | time |  |
| no | Duration | `duration` | time |  |
| no | Note | `note` | text |  |
| no | Add time | `add_time` | date |  |
| no | Assigned to user | `user_id` | user |  |
| no | Creator | `created_by_user_id` | user |  |
| no | Update time | `update_time` | date |  |
| no | Last notification time | `last_notification_time` | date |  |
| no | Location | `location` | address |  |
| no | Latitude of Location | `location_lat` | double |  |
| no | Longitude of Location | `location_long` | double |  |
| no | Apartment/suite no of Location | `location_subpremise` | varchar |  |
| no | House number of Location | `location_street_number` | varchar |  |
| no | Street/road name of Location | `location_route` | varchar |  |
| no | District/sublocality of Location | `location_sublocality` | varchar |  |
| no | City/town/village/locality of Location | `location_locality` | varchar |  |
| no | State/county of Location | `location_admin_area_level_1` | varchar |  |
| no | Region of Location | `location_admin_area_level_2` | varchar |  |
| no | Country of Location | `location_country` | varchar |  |
| no | ZIP/Postal code of Location | `location_postal_code` | varchar |  |
| no | Full/combined address of Location | `location_formatted_address` | varchar |  |
| no | Free/busy | `busy_flag` | enum | Free, Busy |
| no | Public description | `public_description` | text |  |
| no | Lead | `lead_id` | lead |  |
| no | Project | `project_id` | project |  |
| no | Priority | `priority` | enum | Low, Medium, High |

### Product Fields

Endpoint: `productFields`
Total fields: `14`
Likely custom fields: `0`

| Custom | Name | Key | Type | Options |
|---|---|---|---|---|
| no | ID | `id` | int |  |
| no | Name | `name` | varchar |  |
| no | Owner | `owner_id` | user |  |
| no | Product code | `code` | varchar |  |
| no | Active | `selectable` | enum | No, Yes |
| no | Visible to | `visible_to` | visible_to | Item owner, All users |
| no | Price | `price` | double |  |
| no | Unit | `unit` | varchar |  |
| no | Tax | `tax` | double |  |
| no | Description | `description` | text |  |
| no | Category | `category` | enum |  |
| no | Unit prices | `unit_prices` | double |  |
| no | Billing frequency | `billing_frequency` | billing_frequency | One time, Weekly, Monthly, Quarterly, Every 6 months, Annually |
| no | Billing cycles | `billing_frequency_cycles` | int |  |

## Pipelines And Stages

Pipelines: `15`
- CAMILLE - PME-KMU (`id=38`)
  - PROSPECTS (`id=324`, order=1)
  - Call 1 (`id=346`, order=2)
  - Call 2 (`id=327`, order=3)
  - Call 3 (`id=347`, order=4)
  - Call 4 (`id=348`, order=5)
  - Call 5 (`id=349`, order=6)
  - EMAILS (`id=326`, order=7)
  - REFUS (`id=325`, order=8)
  - R1 PRIS (`id=328`, order=9)
  - R1 EFFECTUE (`id=329`, order=10)
  - R2 PRIS (`id=331`, order=11)
  - R2 EFFECTUES (`id=332`, order=12)
  - LOCAL EN ATTENTE (`id=330`, order=13)
  - PERDUES (`id=334`, order=14)
  - CONCLUES (`id=333`, order=15)
- LUDOVIC (`id=1`)
  - PROJETS (`id=1`, order=1)
  - PROSPECTS (`id=91`, order=3)
  - REFUS (`id=104`, order=4)
  - EMAIL (`id=105`, order=5)
  - APPEL (`id=106`, order=6)
  - RDV (`id=2`, order=7)
  - OFFRE A FAIRE (`id=4`, order=8)
  - EN ATTENTE (`id=3`, order=9)
  - CONCLUES (`id=107`, order=10)
- VINCENT (`id=2`)
  - PROSPECTS (`id=8`, order=1)
  - REFUS (`id=14`, order=2)
  - EMAIL (`id=10`, order=3)
  - APPEL (`id=11`, order=4)
  - R1 pris (`id=28`, order=5)
  - R1 effectué (`id=85`, order=6)
  - Local en attente (`id=113`, order=7)
  - R2 pris (`id=77`, order=8)
  - R2 effectué (`id=86`, order=9)
  - PERDUES (`id=317`, order=9)
  - CONCLUES (`id=109`, order=11)
- NICKAL (`id=6`)
  - APPEL (`id=41`, order=1)
  - Rappel (`id=54`, order=2)
  - RDV OK (`id=42`, order=3)
  - REFUS/RAISONS (`id=43`, order=4)
- ALICE PME-KMU (`id=30`)
  - LEADS (`id=244`, order=1)
  - LEADS PRIO (`id=245`, order=2)
  - NRP (`id=246`, order=3)
  - CONTACTÉ - NON DISPO (`id=323`, order=4)
  - RELANCER - SOUS CONTRAT (`id=318`, order=5)
  - RELANCER - BAD TIMING (`id=259`, order=6)
  - R1 PRIS - FABRICE (`id=248`, order=7)
  - NO SHOW (`id=322`, order=8)
  - REFUS (`id=262`, order=9)
- FABRICE DEFI-PME (`id=14`)
  - Prospect (`id=164`, order=1)
  - Refus (`id=127`, order=2)
  - Email (`id=128`, order=3)
  - Appel (`id=129`, order=4)
  - R1 pris (`id=130`, order=5)
  - R1 effectué (`id=131`, order=6)
  - Local en attente (`id=165`, order=7)
  - R2 pris (`id=167`, order=8)
  - R2 effectué (`id=166`, order=9)
  - Conclu (`id=168`, order=10)
- STEPH (`id=8`)
  - PROSPECTS (`id=87`, order=1)
  - REFUS (`id=88`, order=2)
  - EMAIL (`id=89`, order=3)
  - APPEL (`id=90`, order=4)
  - R1 pris (`id=61`, order=5)
  - R1 effectué (`id=56`, order=6)
  - Local en attente (`id=112`, order=7)
  - R2 pris (`id=74`, order=8)
  - R2 effectué (`id=76`, order=9)
  - CONCLUES (`id=108`, order=10)
- PISCIFLOR (`id=9`)
  - Prospect (`id=62`, order=1)
  - Prise de contact effectuée (`id=63`, order=2)
  - Visite planifiée (`id=64`, order=3)
  - Proposition effectuée (`id=65`, order=4)
  - Négociations en cours (`id=66`, order=5)
  - Refus (`id=221`, order=6)
  - SIGNEE (`id=114`, order=7)
- ABBA et REIS INOX (`id=28`)
  - Prospect (`id=222`, order=1)
  - Appel (`id=223`, order=2)
  - Rendez-vous planifié (`id=224`, order=3)
  - Offre faite (`id=225`, order=4)
  - Refus  (`id=227`, order=5)
  - Négociations en cours (`id=226`, order=6)
  - Offre signée (`id=228`, order=7)
- PIERRE (`id=11`)
  - Prospect identifié (`id=80`, order=1)
  - Prise de contact effectuée (`id=81`, order=2)
  - Démonstration planifiée (`id=82`, order=3)
  - Proposition effectuée (`id=83`, order=4)
  - Négociations en cours (`id=84`, order=5)
- SECUFLOR (`id=16`)
  - Lead (`id=142`, order=1)
  - Contact (`id=143`, order=2)
  - Refus (`id=144`, order=3)
  - Rendez-vous pris (`id=145`, order=4)
  - Rendez-vous effectué (`id=148`, order=5)
  - Négociations en cours (`id=146`, order=6)
  - Conclus (`id=147`, order=7)
- ARTUR (`id=22`)
  - PROSPECTS (`id=186`, order=1)
  - REFUS (`id=187`, order=2)
  - EMAIL (`id=188`, order=3)
  - APPEL (`id=189`, order=4)
  - R1 PRIS (`id=190`, order=5)
  - R1 EFFECTUE (`id=278`, order=6)
  - LOCAL EN ATTENTE (`id=279`, order=7)
  - R2 PRIS (`id=280`, order=8)
  - R2 EFFECTUE (`id=281`, order=9)
  - PERDUES (`id=282`, order=10)
  - CONCLUES (`id=283`, order=11)
- KARIM PME-KMU (`id=34`)
  - R1 PRIS (`id=298`, order=1)
  - R1 VALIDE (`id=292`, order=2)
  - R1 FAIT (`id=297`, order=3)
  - R2 PRIS (`id=293`, order=4)
  - R2 FAIT (`id=294`, order=5)
  - R3 (`id=295`, order=6)
  - OFFRE FAITE EN COURS DE SUIVI (`id=296`, order=7)
  - RDV SANS SUITE (`id=299`, order=8)
- TOP (`id=39`)
  - PROSPECTS (`id=335`, order=1)
  - REFUS (`id=336`, order=2)
  - EMAIL (`id=337`, order=3)
  - APPEL 1 (`id=338`, order=4)
  - APPEL 2 (`id=350`, order=5)
  - APPEL 3 (`id=351`, order=6)
  - APPEL 4 (`id=352`, order=7)
  - APPEL 5 (`id=353`, order=8)
  - R1 PRIS (`id=339`, order=9)
  - R1 EFFECTUE (`id=340`, order=10)
  - LOCAL EN ATTENTE (`id=341`, order=11)
  - R2 PRIS (`id=342`, order=12)
  - R2 EFFECTUE (`id=344`, order=13)
  - PERDUES (`id=343`, order=14)
  - CONCLUES (`id=345`, order=15)
- MXM Soumissions (`id=40`)
  - Demandeur (M.O.) (`id=354`, order=1)
  - Appel (`id=355`, order=2)
  - Visite 1 (`id=357`, order=3)
  - Visite 2 (`id=358`, order=4)
  - Refus de MXM (`id=362`, order=5)
  - Soumission transmise (`id=361`, order=6)
  - Perdues (`id=359`, order=7)
  - Conclues (`id=360`, order=8)

## Activity Types

Activity types: `29`
- APPEL 1 (`key_string=appel_1`, active=True)
- APPEL 2 (`key_string=appel_2`, active=True)
- APPEL 3 (`key_string=appel_3`, active=True)
- APPEL 4 (`key_string=appel_4`, active=True)
- APPEL 5 (`key_string=appel_5`, active=True)
- Appel secrétaire  (`key_string=call`, active=True)
- 1er appel décideur (`key_string=nime_appel`, active=True)
- 2ème/Nième appel décideur  (`key_string=2menime_appel_dcideur_`, active=True)
- R1 (`key_string=meeting`, active=True)
- R2 ou plus (`key_string=rdv_2_et_plus`, active=True)
- Envoyer e-mail (`key_string=email`, active=True)
- RDV Suivi client (`key_string=rdv_suivi_client`, active=True)
- RDV Renouvellement Contrat (`key_string=rdv_renouvellement_contrat`, active=True)
- Session cold call I Marion (`key_string=session_cold_call_i_lead_p`, active=False)
- Task (`key_string=task`, active=True)
- Deadline (`key_string=deadline`, active=False)
- Lunch (`key_string=lunch`, active=False)
- Aircall outbound answered call (`key_string=aircall_outbound_answered_`, active=False)
- Aircall outbound unanswered call (`key_string=aircall_outbound_unanswere`, active=False)
- Aircall inbound answered call (`key_string=aircall_inbound_answered_c`, active=False)
- Aircall missed call with voicemail (`key_string=aircall_missed_call_with_v`, active=False)
- Aircall missed call without voicemail (`key_string=aircall_missed_call_withou`, active=False)
- Aircall outbound SMS (`key_string=aircall_outbound_sms`, active=False)
- Aircall inbound SMS (`key_string=aircall_inbound_sms`, active=False)
- Aircall outbound MMS (`key_string=aircall_outbound_mms`, active=False)
- Aircall inbound MMS (`key_string=aircall_inbound_mms`, active=False)
- Aircall inbound WhatsApp message (`key_string=aircall_inbound_whatsapp_m`, active=False)
- Aircall outbound WhatsApp message (`key_string=aircall_outbound_whatsapp_`, active=False)
- 1er Appel (`key_string=1er_appel`, active=False)

## Other Configuration Endpoints

### Users

Endpoint: `users`
Items: `19`

- Alice Favre (`id=24672946`)
- Arnold (`id=14958272`)
- Artur (`id=13177399`)
- Artur Cerqueira (`id=13393717`)
- Camille Monnier (`id=25387110`)
- Fabien Meylan (`id=8934906`)
- Fabrice Käppeli (`id=16047173`)
- Frederic Colonneau (`id=13355643`)
- Gabriel Darbellay (`id=13533805`)
- Julien (`id=12656032`)
- Karim (`id=22446832`)
- Mohsin Kazmi (PME KMU) (`id=14046141`)
- Picard Ludovic (`id=8930692`)
- Pierre Monchatre (`id=11344788`)
- PIRAMEDIA (`id=16047250`)
- Stephane Golliet-Mercier (`id=10145467`)
- Stéphane Golliet-Mercier (`id=8999986`)
- Valentin (`id=22446656`)
- Valentin (`id=25546665`)

### Roles

Endpoint: `roles`
Items: `1`

- (Utilisateurs non affectés) (`id=1`)

### Permission Sets

Endpoint: `permissionSets`
Items: `5`

- Deals admin (`id=869062f1-154c-11ec-8d49-630ebfb1e770`)
- Deals regular user (`id=869062f2-154c-11ec-8d49-630ebfb1e770`)
- Global admin (`id=42353240-dcfa-11ec-9201-cb7990aaa5a2`)
- Global regular user (`id=42f797e0-dcfa-11ec-9201-cb7990aaa5a2`)
- Account settings (`id=439c42f0-ed7a-11ec-b211-03cd07eaaf43`)

### Filters

Endpoint: `filters`
Items: `95`

- Toutes les offres en cours (`id=1`)
- Toutes les offres perdues (`id=3`)
- Offres dépassées (`id=5`)
- Offres vieilles de plus de 3 mois (`id=6`)
- Personnes contactées au cours du dernier mois (`id=7`)
- Organisations contactées au cours du dernier mois (`id=8`)
- Personnes n’ayant pas été contactées au cours du dernier mois (`id=9`)
- Organisations n’ayant pas été contactées au cours du dernier mois (`id=10`)
- Personnes ayant des offres en cours dans le pipeline (`id=11`)
- Organisations avec des offres en cours dans le pipeline (`id=12`)
- Personnes ayant des offres en cours à contacter (`id=13`)
- Organisations ayant des offres en cours à contacter (`id=14`)
- Offre Date de conclusion est plus tard que 31.12.2019 (`id=39`)
- Prospects avec un numéro de téléphone (`id=50`)
- Prospects avec une adresse e-mail (`id=51`)
- Prospects avec un contact lié (`id=52`)
- Prospects ajoutés il y a plus de 3 mois (`id=53`)
- Prospects affectés d'une valeur (`id=54`)
- Prospects avec une activité planifiée (`id=55`)
- Prospects avec une activité en retard (`id=56`)
- Prospects sans activité (`id=57`)
- All statuses (`id=59`)
- Open projects (`id=60`)
- Completed projects (`id=61`)
- Canceled projects (`id=62`)
- Affaires en cours attribuées à des utilisateurs désactivés (`id=83`)
- Prospects attribués à des utilisateurs désactivés (`id=84`)
- Contacts attribués à des utilisateurs désactivés (`id=85`)
- Contacts attribués à des utilisateurs désactivés (`id=86`)
- Activités non effectuées attribuées à des utilisateurs désactivés (`id=87`)
- Undone overdue activities not linked to any item (`id=88`)
- Undone overdue activities linked to items (`id=89`)
- Deals with empty pipeline or stage (`id=99`)
- Affaires en cours sans mise à jour au cours des 12 derniers mois (`id=100`)
- Affaires en cours sans aucune activité liée (`id=101`)
- Affaires en cours n'ayant pas changé d'étape dans le pipeline depuis 3 mois (`id=102`)
- Affaires en cours dont la date de clôture escomptée est dépassée (`id=103`)
- Affaires situées dans la première étape d'un pipeline et n'ayant pas eu de mise à jour dans les 12 derniers mois (`id=104`)
- Prospects âgés de plus d'un mois et n'ayant aucune activité liée (`id=105`)
- Prospects sans mise à jour au cours des 12 derniers mois (`id=106`)
- Personnes ajoutées il y a au moins 12 mois et associées à aucune affaire (`id=107`)
- Personnes sans mise à jour au cours des 12 derniers mois (`id=108`)
- Personnes sans une seule communication e-mail dans les 12 derniers mois (`id=109`)
- Organisations ajoutées il y a au moins 12 mois et associées à aucune affaire (`id=110`)
- Organisations sans mise à jour au cours des 12 derniers mois (`id=111`)
- Activités liées à aucun prospect, affaire, contact ou projet (`id=112`)
- Activités non effectuées et liées à des affaires gagnées ou perdues (`id=113`)
- empty_contacts_system_filter (`id=857`)
- empty_contacts_system_filter (`id=1003`)
- Session call - LEADS PRIO (`id=3348`)
- ...and 45 more

### Currencies

Endpoint: `currencies`
Items: `186`

- Afghanistan Afghani (`id=2`)
- Albanian Lek (`id=3`)
- Algerian Dinar (`id=41`)
- Angolan Kwanza (`id=6`)
- Argentine Peso (`id=7`)
- Armenian Dram (`id=4`)
- Aruban Guilder (`id=9`)
- Australian Dollar (`id=8`)
- Azerbaijan Manat (`id=173`)
- Azerbaijan Old Manat (`id=10`)
- Bahamian Dollar (`id=21`)
- Bahraini Dinar (`id=15`)
- Bangladesh Taka (`id=13`)
- Barbados Dollar (`id=12`)
- Belarusian Ruble (`id=24`)
- Belize Dollar (`id=25`)
- Bermudian Dollar (`id=17`)
- Bhutan Ngultrum (`id=22`)
- Bitcoin (`id=168`)
- Bolivian Boliviano (`id=19`)
- Bolívar Soberano (`id=210`)
- Bolívar Soberano (`id=212`)
- Bosnia and Herzegovina Convertible Marks (`id=11`)
- Botswana Pula (`id=23`)
- Brazilian Real (`id=20`)
- Brunei Dollar (`id=18`)
- Bulgarian Lev (`id=14`)
- Burundi Franc (`id=16`)
- CFA Franc BCEAO (`id=160`)
- CFA Franc BEAC (`id=155`)
- CFP Franc (`id=161`)
- Cambodia Riel (`id=73`)
- Canadian Dollar (`id=26`)
- Cape Verde Escudo (`id=35`)
- Cayman Islands Dollar (`id=78`)
- Chilean Peso (`id=29`)
- Chilean Unidad de Fomento (`id=169`)
- Chinese Yuan Renminbi (`id=30`)
- Colombian Peso (`id=31`)
- Comorian Franc (`id=74`)
- Costa Rican Colon (`id=32`)
- Croatian Kuna (`id=59`)
- Cuban Peso (`id=34`)
- Cyprus Pound (`id=36`)
- Czech Koruna (`id=37`)
- Danish Krone (`id=39`)
- Djibouti Franc (`id=38`)
- Dobra (`id=209`)
- Dominican Peso (`id=40`)
- East Caribbean Dollar (`id=158`)
- ...and 136 more

### Webhooks

Endpoint: `webhooks`
Items: `0`


### Lead Labels

Endpoint: `leadLabels`
Items: `3`

- Hot (`id=39affc70-0c6f-11eb-9cb8-47559434a771`)
- Cold (`id=39affc71-0c6f-11eb-9cb8-47559434a771`)
- Warm (`id=39affc72-0c6f-11eb-9cb8-47559434a771`)

### Lead Sources

Endpoint: `leadSources`
Items: `12`

- Manually created (`id=`)
- Deal (`id=`)
- Web forms (`id=`)
- Prospector (`id=`)
- Leadbooster (`id=`)
- Live chat (`id=`)
- Import (`id=`)
- Website visitors (`id=`)
- Workflow automation (`id=`)
- API (`id=`)
- Messaging inbox (`id=`)
- Campaigns (`id=`)

### Lead Fields

Endpoint: `leadFields`
Items: `38`

- ID (`id=1`)
- Title (`id=2`)
- Labels (`id=3`)
- Source (`id=4`)
- Owner (`id=5`)
- Deal (`id=6`)
- Contact person (`id=7`)
- Organization (`id=8`)
- Person name (`id=9`)
- Person phone (`id=10`)
- Person email (`id=11`)
- Organization name (`id=12`)
- Organization address (`id=13`)
- Lead created (`id=14`)
- Update time (`id=15`)
- Archive time (`id=16`)
- Seen (`id=17`)
- Value (`id=18`)
- Currency (`id=19`)
- Creator (`id=20`)
- Expected close date (`id=21`)
- Visible to (`id=22`)
- Source reference ID (`id=23`)
- Next activity status (`id=27`)
- Next activity (`id=28`)
- Next activity date (`id=29`)
- Source origin (`id=30`)
- Source origin ID (`id=31`)
- Source channel (`id=32`)
- Source channel ID (`id=33`)
- Archive status (`id=36`)
- Origine prospect (`id=24`)
- Pipeline (`id=34`)
- Responsable 1 (`id=38`)
- Téléphone 1 (`id=39`)
- Fonction Responsable  1 (`id=40`)
- Fonction Responsable 2 (`id=41`)
- Responsable 2 (`id=42`)

## Export Errors

- `teams`: teams: Teams feature is not enabled in your company
- `dealLabels`: dealLabels: Not Found
- `organizationRelationships`: organizationRelationships: Missing required org_id
