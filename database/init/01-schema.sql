SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- ============================================================
-- SCHÉMA COMPLET DE LA BASE DE DONNÉES
-- Chatbot Signalement — Centre Informatique UGANC
-- Version: 2.0
-- ============================================================

CREATE DATABASE IF NOT EXISTS chatbot_signalement
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE chatbot_signalement;

-- ============================================================
-- 1. Rôles utilisateurs
-- ============================================================
CREATE TABLE roles (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(50)  NOT NULL UNIQUE,
    description VARCHAR(255) NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================
-- 2. Utilisateurs (étudiants, techniciens, admin)
-- L'admin est créé en dur dans le seed.
-- Les comptes étudiants et techniciens sont créés uniquement
-- par l'admin via le dashboard.
-- ============================================================
CREATE TABLE users (
    id                    INT AUTO_INCREMENT PRIMARY KEY,
    role_id               INT          NOT NULL,
    student_id            VARCHAR(20)  NULL UNIQUE COMMENT 'Numéro étudiant (pour les étudiants uniquement)',
    username              VARCHAR(50)  NULL UNIQUE COMMENT 'Nom d''utilisateur (pour connexion étudiants)',
    genre                 CHAR(1)      NULL COMMENT 'Genre : M (Masculin) ou F (Féminin)',
    niveau_etude          VARCHAR(5)   NULL COMMENT 'Niveau : L1, L2, L3, M1, M2',
    programme             VARCHAR(50)  NULL COMMENT 'Programme : Développement logiciel ou NTIC',
    first_name            VARCHAR(100) NOT NULL,
    last_name             VARCHAR(100) NOT NULL,
    email                 VARCHAR(255) NULL UNIQUE,
    phone                 VARCHAR(20)  NULL,
    password_hash         VARCHAR(255) NOT NULL,
    is_active             BOOLEAN      NOT NULL DEFAULT TRUE COMMENT 'Faux si l''admin a désactivé le compte',
    created_by            INT          NULL COMMENT 'Admin qui a créé ce compte (NULL pour l''admin lui-même)',
    last_login_at         TIMESTAMP    NULL,
    failed_login_attempts INT          NOT NULL DEFAULT 0,
    locked_until          TIMESTAMP    NULL COMMENT 'Compte verrouillé jusqu''à cette date (tentatives échouées)',
    password_changed_at   TIMESTAMP    NULL,
    created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_user_role    FOREIGN KEY (role_id)     REFERENCES roles(id),
    CONSTRAINT fk_user_creator FOREIGN KEY (created_by)  REFERENCES users(id)
) ENGINE=InnoDB;

CREATE INDEX idx_users_role       ON users(role_id);
CREATE INDEX idx_users_student_id ON users(student_id);
CREATE INDEX idx_users_active     ON users(is_active);

-- ============================================================
-- 3. Jetons de réinitialisation de mot de passe
-- ============================================================
CREATE TABLE password_reset_tokens (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT          NOT NULL,
    token       VARCHAR(255) NOT NULL,
    expires_at  TIMESTAMP    NOT NULL,
    used_at     TIMESTAMP    NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_reset_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE INDEX idx_reset_token ON password_reset_tokens(token);

-- ============================================================
-- 4. Sessions utilisateur (gestion des jetons JWT)
-- ============================================================
CREATE TABLE user_sessions (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    user_id       INT          NOT NULL,
    access_token  VARCHAR(500) NOT NULL,
    refresh_token VARCHAR(500) NULL,
    expires_at    TIMESTAMP    NOT NULL,
    ip_address    VARCHAR(45)  NULL,
    user_agent    VARCHAR(500) NULL,
    is_revoked    BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_session_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE INDEX idx_session_user  ON user_sessions(user_id);
CREATE INDEX idx_session_token ON user_sessions(access_token(255));

-- ============================================================
-- 5. Bâtiments
-- ============================================================
CREATE TABLE buildings (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    code        VARCHAR(20)  NOT NULL UNIQUE COMMENT 'Code court du bâtiment',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================
-- 6. Salles / Laboratoires
-- ============================================================
CREATE TABLE rooms (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    building_id   INT          NULL COMMENT 'Optionnel, bâtiment en référence',
    building_name VARCHAR(100) NULL COMMENT 'Nom du bâtiment en texte libre',
    name          VARCHAR(100) NOT NULL COMMENT 'Nom de la salle ou du laboratoire',
    floor         INT          NULL COMMENT 'Étage',
    room_type     ENUM('lab', 'classroom', 'office', 'multimedia', 'other') NOT NULL DEFAULT 'other',
    is_active     BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_room_building FOREIGN KEY (building_id) REFERENCES buildings(id)
) ENGINE=InnoDB;

CREATE INDEX idx_rooms_building ON rooms(building_id);
CREATE INDEX idx_rooms_active   ON rooms(is_active);

-- ============================================================
-- 7. Catégories de problèmes
-- ============================================================
CREATE TABLE problem_categories (
    id               INT AUTO_INCREMENT PRIMARY KEY,
    name             VARCHAR(100) NOT NULL,
    description      TEXT         NULL,
    icon             VARCHAR(50)  NULL COMMENT 'Icône ou émoji représentatif',
    priority_default ENUM('low', 'medium', 'high') NOT NULL DEFAULT 'medium',
    is_active        BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================
-- 8. Sous-catégories de problèmes (pour le diagnostic fin
--    via le chatbot, ex: "Matériel" -> "Écran", "Clavier", etc.)
-- ============================================================
CREATE TABLE problem_subcategories (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT          NOT NULL,
    name        VARCHAR(100) NOT NULL,
    description TEXT         NULL,
    sort_order  INT          NOT NULL DEFAULT 0,
    is_active   BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_subcat_category FOREIGN KEY (category_id) REFERENCES problem_categories(id)
) ENGINE=InnoDB;

CREATE INDEX idx_subcat_category ON problem_subcategories(category_id);

-- ============================================================
-- 9. Questions du chatbot (flux conversationnel paramétrable
--    par l'admin, ex: "Depuis quand ?", "Avez-vous redémarré ?")
-- ============================================================
CREATE TABLE chatbot_questions (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    category_id     INT          NULL COMMENT 'NULL = question generique, sinon liee a une categorie',
    subcategory_id  INT          NULL,
    question_text   VARCHAR(500) NOT NULL,
    question_type   ENUM('text', 'select', 'yes_no', 'multiline') NOT NULL DEFAULT 'text',
    sort_order      INT          NOT NULL DEFAULT 0,
    is_required     BOOLEAN      NOT NULL DEFAULT FALSE,
    is_active       BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_question_category    FOREIGN KEY (category_id)    REFERENCES problem_categories(id),
    CONSTRAINT fk_question_subcategory FOREIGN KEY (subcategory_id) REFERENCES problem_subcategories(id)
) ENGINE=InnoDB;

CREATE INDEX idx_questions_category ON chatbot_questions(category_id);

-- ============================================================
-- 10. Options pour les questions de type 'select'
-- ============================================================
CREATE TABLE chatbot_question_options (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    question_id INT          NOT NULL,
    option_text VARCHAR(255) NOT NULL,
    sort_order  INT          NOT NULL DEFAULT 0,
    CONSTRAINT fk_option_question FOREIGN KEY (question_id) REFERENCES chatbot_questions(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- 11. Statuts des tickets (flux: Soumis -> Assigné -> En cours
--     -> En attente -> Résolu)
-- ============================================================
CREATE TABLE ticket_statuses (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(50)  NOT NULL UNIQUE,
    label       VARCHAR(100) NOT NULL,
    sort_order  INT          NOT NULL DEFAULT 0,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ============================================================
-- 12. Tickets (signalements de pannes)
-- ============================================================
CREATE TABLE tickets (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    ticket_number       VARCHAR(20)  NOT NULL UNIQUE COMMENT 'Identifiant public (ex: TKT-00042)',
    user_id             INT          NOT NULL COMMENT 'Étudiant qui a créé le ticket',
    category_id         INT          NOT NULL,
    subcategory_id      INT          NULL,
    room_id             INT          NOT NULL,
    workstation_number  VARCHAR(50)  NULL COMMENT 'Numéro du poste de travail concerné',
    description         TEXT         NULL COMMENT 'Description libre (max 500 car.)',
    status_id           INT          NOT NULL,
    assigned_to         INT          NULL COMMENT 'Technicien assigné',
    priority            ENUM('low', 'medium', 'high', 'critical') NOT NULL DEFAULT 'medium',
    source              ENUM('chatbot', 'dashboard', 'api') NOT NULL DEFAULT 'chatbot',
    sla_deadline        TIMESTAMP    NULL COMMENT 'Délai de résolution selon priorité',
    escalated_at        TIMESTAMP    NULL COMMENT 'Date d''escalade si non pris en charge',
    resolution_notes    TEXT         NULL COMMENT 'Notes du technicien sur la résolution',
    closed_by           INT          NULL COMMENT 'Qui a clôturé le ticket',
    is_duplicate_of     INT          NULL COMMENT 'Ticket parent si celui-ci est un doublon',
    reminder_sent       BOOLEAN      NOT NULL DEFAULT FALSE COMMENT 'Rappel 24h envoyé ?',
    created_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at          TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    resolved_at         TIMESTAMP    NULL,
    CONSTRAINT fk_ticket_user         FOREIGN KEY (user_id)         REFERENCES users(id),
    CONSTRAINT fk_ticket_category     FOREIGN KEY (category_id)     REFERENCES problem_categories(id),
    CONSTRAINT fk_ticket_subcategory  FOREIGN KEY (subcategory_id)  REFERENCES problem_subcategories(id),
    CONSTRAINT fk_ticket_room         FOREIGN KEY (room_id)         REFERENCES rooms(id),
    CONSTRAINT fk_ticket_status       FOREIGN KEY (status_id)       REFERENCES ticket_statuses(id),
    CONSTRAINT fk_ticket_technician   FOREIGN KEY (assigned_to)     REFERENCES users(id),
    CONSTRAINT fk_ticket_closed_by    FOREIGN KEY (closed_by)       REFERENCES users(id),
    CONSTRAINT fk_ticket_duplicate    FOREIGN KEY (is_duplicate_of) REFERENCES tickets(id)
) ENGINE=InnoDB;

CREATE INDEX idx_tickets_user       ON tickets(user_id);
CREATE INDEX idx_tickets_status     ON tickets(status_id);
CREATE INDEX idx_tickets_assigned   ON tickets(assigned_to);
CREATE INDEX idx_tickets_category   ON tickets(category_id);
CREATE INDEX idx_tickets_room       ON tickets(room_id);
CREATE INDEX idx_tickets_created    ON tickets(created_at);
CREATE INDEX idx_tickets_priority   ON tickets(priority);
CREATE INDEX idx_tickets_source     ON tickets(source);
CREATE INDEX idx_tickets_sla        ON tickets(sla_deadline);

-- ============================================================
-- 13. Pièces jointes des tickets (photos, captures d'écran)
-- ============================================================
CREATE TABLE ticket_attachments (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    ticket_id   INT          NOT NULL,
    file_name   VARCHAR(255) NOT NULL,
    file_path   VARCHAR(500) NOT NULL,
    file_size   INT          NULL COMMENT 'Taille en octets',
    mime_type   VARCHAR(100) NULL,
    uploaded_by INT          NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_attach_ticket FOREIGN KEY (ticket_id)    REFERENCES tickets(id) ON DELETE CASCADE,
    CONSTRAINT fk_attach_user   FOREIGN KEY (uploaded_by)  REFERENCES users(id)
) ENGINE=InnoDB;

CREATE INDEX idx_attachments_ticket ON ticket_attachments(ticket_id);

-- ============================================================
-- 14. Historique des changements de statut
-- ============================================================
CREATE TABLE ticket_status_history (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    ticket_id   INT          NOT NULL,
    from_status INT          NULL,
    to_status   INT          NOT NULL,
    changed_by  INT          NOT NULL,
    comment     TEXT         NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_history_ticket      FOREIGN KEY (ticket_id)      REFERENCES tickets(id) ON DELETE CASCADE,
    CONSTRAINT fk_history_from_status FOREIGN KEY (from_status)    REFERENCES ticket_statuses(id),
    CONSTRAINT fk_history_to_status   FOREIGN KEY (to_status)      REFERENCES ticket_statuses(id),
    CONSTRAINT fk_history_user        FOREIGN KEY (changed_by)     REFERENCES users(id)
) ENGINE=InnoDB;

CREATE INDEX idx_history_ticket ON ticket_status_history(ticket_id);

-- ============================================================
-- 15. Messages (chat entre étudiant et technicien)
-- ============================================================
CREATE TABLE ticket_messages (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    ticket_id      INT          NOT NULL,
    sender_id      INT          NOT NULL,
    message        TEXT         NOT NULL,
    message_type   VARCHAR(20)  NOT NULL DEFAULT 'text' COMMENT 'text, audio, file',
    is_deleted     BOOLEAN      NOT NULL DEFAULT FALSE,
    attachment_id  INT          NULL,
    is_read        BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_message_ticket  FOREIGN KEY (ticket_id)     REFERENCES tickets(id) ON DELETE CASCADE,
    CONSTRAINT fk_message_sender  FOREIGN KEY (sender_id)     REFERENCES users(id),
    CONSTRAINT fk_message_attach  FOREIGN KEY (attachment_id) REFERENCES ticket_attachments(id) ON DELETE SET NULL
) ENGINE=InnoDB;

CREATE INDEX idx_messages_ticket    ON ticket_messages(ticket_id);
CREATE INDEX idx_messages_read      ON ticket_messages(is_read);
CREATE INDEX idx_messages_deleted   ON ticket_messages(is_deleted);

-- ============================================================
-- 16. Évaluations (feedback après résolution)
-- ============================================================
CREATE TABLE evaluations (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    ticket_id   INT          NOT NULL UNIQUE,
    user_id     INT          NOT NULL,
    rating      TINYINT      NOT NULL COMMENT '1=Insatisfait, 2=Moyen, 3=Satisfait',
    comment     TEXT         NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_eval_ticket FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE,
    CONSTRAINT fk_eval_user   FOREIGN KEY (user_id)   REFERENCES users(id)
) ENGINE=InnoDB;

-- ============================================================
-- 17. Notifications
-- ============================================================
CREATE TABLE notifications (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT          NOT NULL,
    ticket_id   INT          NULL,
    type        VARCHAR(50)  NOT NULL COMMENT 'new_ticket, status_change, assignment, reminder, feedback_request',
    title       VARCHAR(255) NOT NULL,
    message     TEXT         NULL,
    is_read     BOOLEAN      NOT NULL DEFAULT FALSE,
    is_email    BOOLEAN      NOT NULL DEFAULT FALSE COMMENT 'Email envoyé ?',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_notif_user   FOREIGN KEY (user_id)   REFERENCES users(id),
    CONSTRAINT fk_notif_ticket FOREIGN KEY (ticket_id) REFERENCES tickets(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE INDEX idx_notifications_user    ON notifications(user_id, is_read);
CREATE INDEX idx_notifications_created ON notifications(created_at);
CREATE INDEX idx_notifications_type    ON notifications(type);

-- ============================================================
-- 18. Préférences de notification par utilisateur
-- ============================================================
CREATE TABLE notification_preferences (
    id                   INT AUTO_INCREMENT PRIMARY KEY,
    user_id              INT      NOT NULL UNIQUE,
    email_notifications  BOOLEAN  NOT NULL DEFAULT TRUE,
    in_app_notifications BOOLEAN  NOT NULL DEFAULT TRUE,
    sms_notifications    BOOLEAN  NOT NULL DEFAULT FALSE,
    notify_new_ticket    BOOLEAN  NOT NULL DEFAULT TRUE,
    notify_status_change BOOLEAN  NOT NULL DEFAULT TRUE,
    notify_assignment    BOOLEAN  NOT NULL DEFAULT TRUE,
    notify_reminder      BOOLEAN  NOT NULL DEFAULT TRUE,
    created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_pref_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ============================================================
-- 19. Journal d'audit (traçabilité des actions admin)
-- ============================================================
CREATE TABLE audit_log (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT          NOT NULL COMMENT 'Admin qui a effectué l''action',
    action      VARCHAR(100) NOT NULL COMMENT 'create, update, delete, activate, deactivate',
    entity_type VARCHAR(50)  NOT NULL COMMENT 'user, room, category, ticket, etc.',
    entity_id   INT          NULL,
    old_values  JSON         NULL,
    new_values  JSON         NULL,
    ip_address  VARCHAR(45)  NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_audit_user FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB;

CREATE INDEX idx_audit_user   ON audit_log(user_id);
CREATE INDEX idx_audit_action ON audit_log(action, entity_type);
CREATE INDEX idx_audit_date   ON audit_log(created_at);

-- ============================================================
-- 20. Configuration système (paramètres modifiables par l'admin)
-- ============================================================
CREATE TABLE system_config (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    config_key    VARCHAR(100) NOT NULL UNIQUE,
    config_value  TEXT         NOT NULL,
    description   VARCHAR(255) NULL,
    updated_by    INT          NULL,
    updated_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_config_user FOREIGN KEY (updated_by) REFERENCES users(id)
) ENGINE=InnoDB;
