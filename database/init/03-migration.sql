SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

USE chatbot_signalement;

-- Safely add columns only if they don't exist
SET @col_exists = (SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = 'chatbot_signalement' AND TABLE_NAME = 'ticket_messages' AND COLUMN_NAME = 'message_type');

SET @sql = IF(@col_exists = 0,
  'ALTER TABLE ticket_messages
    ADD COLUMN message_type   VARCHAR(20)  NOT NULL DEFAULT ''text'' AFTER message,
    ADD COLUMN is_deleted     BOOLEAN      NOT NULL DEFAULT FALSE AFTER message_type,
    ADD COLUMN attachment_id  INT          NULL AFTER is_deleted,
    ADD INDEX idx_messages_deleted (is_deleted),
    ADD CONSTRAINT fk_message_attach FOREIGN KEY (attachment_id) REFERENCES ticket_attachments(id) ON DELETE SET NULL',
  'SELECT 1'
);

PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
