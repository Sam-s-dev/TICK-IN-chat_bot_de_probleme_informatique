SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- ============================================================
-- DONNÉES DE DÉMONSTRATION (SEED)
-- Chatbot Signalement — Centre Informatique UGANC
-- Version: 2.0
--
-- Tous les mots de passe par défaut : "password123"
-- Hash bcrypt (Python/passlib) : $2b$12$jR1Zsod8TB0poMb9VL3dj.y//wGagtdbIcn4QQiF6g888/LU70xJu
-- ============================================================

USE chatbot_signalement;

-- ============================================================
-- 1. Rôles
-- ============================================================
INSERT INTO roles (name, description) VALUES
    ('admin',      'Administrateur du système — gère les utilisateurs, salles, catégories et consulte les statistiques'),
    ('technicien', 'Technicien du Centre Informatique — reçoit, traite et résout les tickets'),
    ('etudiant',   'Étudiant de l\'UGANC — signale les pannes via le chatbot et suit ses tickets');

-- ============================================================
-- 2. Utilisateurs
-- 2a. Admin (créé en dur — c'est le seul compte créé manuellement)
-- 2b. Techniciens (créés par l'admin)
-- 2c. Étudiants (créés par l'admin)
-- ============================================================

-- Admin : compte root du système, créé manuellement (created_by = NULL)
INSERT INTO users (role_id, first_name, last_name, email, phone, password_hash, is_active, created_by) VALUES
    (1, 'Moussa',   'Kaba',   'admin@centre-info.uganc.edu.gn',    '626-404-040',
     '$2b$12$jR1Zsod8TB0poMb9VL3dj.y//wGagtdbIcn4QQiF6g888/LU70xJu',
     TRUE, NULL);

-- Techniciens (créés par l'admin, id=1)
INSERT INTO users (role_id, first_name, last_name, email, phone, password_hash, is_active, created_by) VALUES
    (2, 'Alpha Oumar', 'Diallo', 'alpha.diallo@centre-info.uganc.edu.gn', '626-101-010',
     '$2b$12$jR1Zsod8TB0poMb9VL3dj.y//wGagtdbIcn4QQiF6g888/LU70xJu',
     TRUE, 1),
    (2, 'Sékou',       'Condé',  'sekou.conde@centre-info.uganc.edu.gn',  '626-202-020',
     '$2b$12$jR1Zsod8TB0poMb9VL3dj.y//wGagtdbIcn4QQiF6g888/LU70xJu',
     TRUE, 1),
    (2, 'Kadiatou',    'Sylla',  'kadiatou.sylla@centre-info.uganc.edu.gn','626-303-030',
     '$2b$12$jR1Zsod8TB0poMb9VL3dj.y//wGagtdbIcn4QQiF6g888/LU70xJu',
     TRUE, 1);

-- Étudiants (créés par l'admin, id=1)
INSERT INTO users (role_id, student_id, first_name, last_name, email, phone, password_hash, is_active, created_by) VALUES
    (3, 'ETU-2024-001', 'Fatoumata', 'Diallo',  'fatoumata.diallo@uganc.edu.gn',  '621-111-111',
     '$2b$12$jR1Zsod8TB0poMb9VL3dj.y//wGagtdbIcn4QQiF6g888/LU70xJu',
     TRUE, 1),
    (3, 'ETU-2024-002', 'Mamadou',   'Bah',     'mamadou.bah@uganc.edu.gn',       '622-222-222',
     '$2b$12$jR1Zsod8TB0poMb9VL3dj.y//wGagtdbIcn4QQiF6g888/LU70xJu',
     TRUE, 1),
    (3, 'ETU-2024-003', 'Aminata',   'Sow',     'aminata.sow@uganc.edu.gn',        '623-333-333',
     '$2b$12$jR1Zsod8TB0poMb9VL3dj.y//wGagtdbIcn4QQiF6g888/LU70xJu',
     TRUE, 1),
    (3, 'ETU-2024-004', 'Ibrahima',  'Camara',  'ibrahima.camara@uganc.edu.gn',    '624-444-444',
     '$2b$12$jR1Zsod8TB0poMb9VL3dj.y//wGagtdbIcn4QQiF6g888/LU70xJu',
     TRUE, 1),
    (3, 'ETU-2024-005', 'Mariame',   'Barry',   'mariame.barry@uganc.edu.gn',      '625-555-555',
     '$2b$12$jR1Zsod8TB0poMb9VL3dj.y//wGagtdbIcn4QQiF6g888/LU70xJu',
     TRUE, 1);

-- ============================================================
-- 3. Bâtiments
-- ============================================================
INSERT INTO buildings (name, code) VALUES
    ('Bâtiment Principal — Centre Informatique', 'A'),
    ('Bâtiment des Laboratoires',                'B'),
    ('Bibliothèque Numérique',                   'C');

-- ============================================================
-- 4. Salles
-- ============================================================
INSERT INTO rooms (building_name, name, floor, room_type) VALUES
    ('Bâtiment A', 'Salle TP 1',       0, 'lab'),
    ('Bâtiment A', 'Salle TP 2',       0, 'lab'),
    ('Bâtiment A', 'Salle TP 3',       1, 'lab'),
    ('Bâtiment A', 'Laboratoire 1',    1, 'lab'),
    ('Bâtiment A', 'Laboratoire 2',    1, 'lab'),
    ('Bâtiment A', 'Salle de Cours 1', 2, 'classroom'),
    ('Bâtiment A', 'Salle de Cours 2', 2, 'classroom'),
    ('Bâtiment B', 'Salle de Cours A', 0, 'classroom'),
    ('Bâtiment B', 'Salle de Cours B', 0, 'classroom'),
    ('Bâtiment B', 'Labo Réseau',      1, 'lab'),
    (NULL, 'Amphi A',   0, 'classroom'),
    (NULL, 'Amphi B',   1, 'classroom'),
    (NULL, 'Espace Numérique',  0, 'multimedia'),
    (NULL, 'Salle Multimédia',  1, 'multimedia');

-- ============================================================
-- 5. Catégories de problèmes
-- ============================================================
INSERT INTO problem_categories (name, description, icon, priority_default) VALUES
    ('Matériel',       'Problèmes matériels : écran, clavier, souris, alimentation, poste qui ne démarre pas',       '🖥️', 'high'),
    ('Logiciel',       'Problèmes logiciels : application bloquée, OS corrompu, virus, pilote manquant',             '💿', 'medium'),
    ('Réseau / Internet', 'Problèmes réseau : Wi-Fi coupé, connexion lente, câble débranché, sites bloqués',        '🌐', 'high'),
    ('Périphériques',  'Problèmes périphériques : imprimante, scanner, vidéoprojecteur, prise électrique',           '🖨️', 'medium');

-- ============================================================
-- 6. Sous-catégories
-- ============================================================
INSERT INTO problem_subcategories (category_id, name, description, sort_order) VALUES
    (1, 'Écran',        'Écran noir, lignes, flicker, cassé',          1),
    (1, 'Clavier',      'Touches qui ne fonctionnent pas, clavier mort',2),
    (1, 'Souris',       'Souris USB ou sans fil ne répond pas',         3),
    (1, 'Alimentation', 'Poste ne s''allume pas, chargeur défectueux',  4),
    (1, 'Autre',        'Autre problème matériel',                      5),
    (2, 'Application',  'Application qui ne s''ouvre pas ou plante',    1),
    (2, 'Système',      'OS lent, écran bleu, mise à jour bloquée',     2),
    (2, 'Virus',        'Antivirus, malware, comportement suspect',     3),
    (2, 'Pilote',       'Pilote manquant ou obsolète',                  4),
    (2, 'Autre',        'Autre problème logiciel',                      5),
    (3, 'Wi-Fi',        'Connexion Wi-Fi coupée ou absente',            1),
    (3, 'Câble',        'Câble réseau débranché ou défectueux',         2),
    (3, 'Lenteur',      'Connexion anormalement lente',                 3),
    (3, 'Site bloqué',  'Accès à certains sites impossible',            4),
    (3, 'Autre',        'Autre problème réseau',                        5),
    (4, 'Imprimante',   'Imprimante hors service, bourrage papier',     1),
    (4, 'Scanner',      'Scanner non détecté ou ne fonctionne pas',     2),
    (4, 'Vidéoprojecteur','Image absente ou de mauvaise qualité',       3),
    (4, 'Prise',        'Prise électrique ne fonctionne pas',           4),
    (4, 'Autre',        'Autre problème périphérique',                  5);

-- ============================================================
-- 7. Questions du chatbot (flux conversationnel)
-- ============================================================
INSERT INTO chatbot_questions (category_id, subcategory_id, question_text, question_type, sort_order, is_required) VALUES
    (NULL, NULL, 'De quel type de problème s''agit-il ?',                             'select', 1, TRUE),
    (1,    NULL, 'Quel équipement matériel est concerné ?',                           'select', 2, TRUE),
    (1,    NULL, 'Depuis quand le problème est-il présent ?',                         'select', 3, TRUE),
    (1,    NULL, 'Avez-vous déjà redémarré le poste ?',                               'yes_no', 4, TRUE),
    (2,    NULL, 'Quelle application ou logiciel est concerné ?',                      'text',   2, TRUE),
    (2,    NULL, 'Avez-vous essayé de redémarrer l''application ?',                   'yes_no', 3, TRUE),
    (2,    NULL, 'Y a-t-il un message d''erreur ? Si oui, lequel ?',                  'text',   4, FALSE),
    (3,    NULL, 'Quel type de problème réseau rencontrez-vous ?',                    'select', 2, TRUE),
    (3,    NULL, 'Le problème concerne-t-il tous les appareils ou un seul ?',         'select', 3, TRUE),
    (4,    NULL, 'Quel périphérique est concerné ?',                                  'select', 2, TRUE),
    (4,    NULL, 'Le périphérique est-il allumé et correctement branché ?',           'yes_no', 3, TRUE);

-- ============================================================
-- 8. Options pour les questions de type 'select'
-- ============================================================
INSERT INTO chatbot_question_options (question_id, option_text, sort_order) VALUES
    -- Question 1 : type de problème (générique)
    (1, '🖥️ Matériel',       1),
    (1, '💿 Logiciel',       2),
    (1, '🌐 Réseau / Internet', 3),
    (1, '🖨️ Périphériques',  4),
    -- Question 2 : équipement matériel
    (2, 'Écran',             1),
    (2, 'Clavier',           2),
    (2, 'Souris',            3),
    (2, 'Unité centrale',    4),
    (2, 'Alimentation / chargeur', 5),
    (2, 'Autre',             6),
    -- Question 3 : depuis quand
    (3, 'Aujourd''hui',       1),
    (3, 'Depuis hier',        2),
    (3, 'Depuis plusieurs jours', 3),
    (3, 'Je ne sais pas',     4),
    -- Question 8 : type de problème réseau
    (8, 'Pas de connexion Wi-Fi',    1),
    (8, 'Connexion lente',           2),
    (8, 'Câble réseau débranché',    3),
    (8, 'Accès à certains sites bloqué', 4),
    (8, 'Autre',                     5),
    -- Question 9 : tous ou un seul appareil
    (9, 'Tous les appareils',     1),
    (9, 'Un seul poste',          2),
    (9, 'Je ne sais pas',         3),
    -- Question 10 : quel périphérique
    (10, 'Imprimante',           1),
    (10, 'Scanner',              2),
    (10, 'Vidéoprojecteur',      3),
    (10, 'Prise électrique',     4),
    (10, 'Autre',                5);

-- ============================================================
-- 9. Statuts des tickets
-- ============================================================
INSERT INTO ticket_statuses (name, label, sort_order) VALUES
    ('submitted',   'Soumis',      1),
    ('assigned',    'Assigné',     2),
    ('in_progress', 'En cours',    3),
    ('pending',     'En attente',  4),
    ('resolved',    'Résolu',      5);

-- ============================================================
-- 10. Configuration système (paramètres par défaut)
-- ============================================================
INSERT INTO system_config (config_key, config_value, description, updated_by) VALUES
    ('sla_hours_low',       '72',  'Délai de résolution en heures pour les priorités basses',      1),
    ('sla_hours_medium',    '48',  'Délai de résolution en heures pour les priorités moyennes',    1),
    ('sla_hours_high',      '24',  'Délai de résolution en heures pour les priorités hautes',      1),
    ('sla_hours_critical',  '4',   'Délai de résolution en heures pour les priorités critiques',   1),
    ('reminder_hours',      '24',  'Heures avant envoi d''un rappel pour ticket non pris en charge', 1),
    ('max_login_attempts',  '5',   'Tentatives de connexion avant verrouillage',                   1),
    ('lockout_minutes',     '30',  'Durée de verrouillage en minutes après échecs',                1),
    ('ticket_prefix',       'TKT', 'Préfixe des numéros de ticket',                                1),
    ('max_photo_size_mb',   '2',   'Taille maximale des photos uploadées (Mo)',                    1),
    ('allowed_mime_types',  'image/jpeg,image/png,image/gif,application/pdf', 'Types MIME autorisés', 1);

-- ============================================================
-- 11. PrǸfǸrences de notification
-- ============================================================
INSERT INTO notification_preferences (user_id) VALUES
    (1), (2), (3), (4), (5), (6), (7), (8), (9);
