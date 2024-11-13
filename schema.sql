
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE,
    password TEXT,
    visible BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE groups (
    id SERIAL PRIMARY KEY,
    name TEXT,
    visible BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE group_roles (
    id SERIAL PRIMARY KEY,
    group_id INTEGER REFERENCES groups,
    user_id INTEGER REFERENCES users,
    is_creator BOOLEAN NOT NULL,
    role INTEGER
);

CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    group_id INTEGER REFERENCES groups,
    visible BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects,
    title TEXT,
    description TEXT,
    state TEXT,
    deadline TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE,
    visible BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE task_assignments (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES tasks,
    user_id INTEGER REFERENCES users
);
