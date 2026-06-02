SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

USE chatbot_signalement;

CREATE TABLE IF NOT EXISTS testimonials (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    role        VARCHAR(100) NOT NULL,
    text        TEXT         NOT NULL,
    stars       TINYINT      NOT NULL DEFAULT 5,
    is_active   BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS faqs (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    question    VARCHAR(500) NOT NULL,
    answer      TEXT         NOT NULL,
    sort_order  INT          NOT NULL DEFAULT 0,
    is_active   BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

INSERT INTO testimonials (name, role, text, stars) VALUES
('Mohamed Sams Deen Camara', 'Etudiant', 'Super plateforme ! J ai signale un probleme de connexion et en 30 minutes c etait regle.', 5),
('Tiguidanke Nabe', 'Etudiante', 'Le suivi en temps reel est tres pratique. Je sais exactement ou en est ma demande.', 5),
('Aissatou Bah', 'Technicienne', 'La messagerie integree facilite vraiment les echanges avec les etudiants.', 4);

INSERT INTO faqs (question, answer, sort_order) VALUES
('Comment creer un compte ?', 'Les etudiants peuvent creer leur compte directement depuis la page d inscription avec leur adresse @uganc.edu.gn. Pour les comptes administrateurs et techniciens, contactez l administration du Centre Informatique.', 1),
('Quels types de problemes puis-je signaler ?', 'Problemes materiels (PC, imprimante, reseau), logiciels (bugs, installations), acces (comptes, mots de passe), ou salles informatiques.', 2),
('Comment suivre l avancement de mon ticket ?', 'Connectez-vous a votre espace etudiant. Vous verrez la liste de vos tickets avec leur statut (Ouvert, En cours, Resolu, etc.) et les messages de votre technicien.', 3),
('Que faire si mon probleme est urgent ?', 'Ouvrez un ticket en selectionnant "Urgent" dans le niveau de priorite. L equipe technique sera notifiee immediatement.', 4),
('Puis-je laisser un avis apres la resolution ?', 'Oui ! Apres la resolution de votre ticket, vous pouvez evaluer la qualite du service et laisser un commentaire.', 5);
