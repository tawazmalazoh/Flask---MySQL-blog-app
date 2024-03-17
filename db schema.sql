

CREATE DATABASE blog;

CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS posts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    category_id INT,
    image VARCHAR(255), 
    added_by VARCHAR(255) DEFAULT 'Tawanda Dadirai',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(id)
);



CREATE TABLE IF NOT EXISTS comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT NOT NULL,
    body TEXT NOT NULL,
    added_by VARCHAR(255) DEFAULT 'Anonymous',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (post_id) REFERENCES posts(id)
);


-- We are inserting the categories which the blog supports
INSERT INTO categories (name) 
VALUES 
('Technology'), 
('Environment'), 
('Health'), 
('Travel'), 
('Food'), 
('Lifestyle'), 
('Fashion'), 
('Finance'), 
('Sports'), 
('Entertainment');



