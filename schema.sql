
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    visible BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE groups (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    visible BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE group_roles (
    id SERIAL PRIMARY KEY,
    group_id INTEGER REFERENCES groups,
    user_id INTEGER REFERENCES users,
    role TEXT NOT NULL -- meaning defined in enums.py file
);

CREATE TABLE group_invites (
    id SERIAL PRIMARY KEY,
    group_id INTEGER REFERENCES groups,
    invitee_id INTEGER REFERENCES users,
    role TEXT NOT NULL -- meaning defined in enums.py file
);

CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    group_id INTEGER REFERENCES groups,
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    archived BOOLEAN NOT NULL DEFAULT FALSE,
    visible BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    created_by_id INTEGER REFERENCES users,
    project_id INTEGER REFERENCES projects,
    title TEXT,
    description TEXT,
    state TEXT DEFAULT 'Pending', -- meaning defined in enums.py file
    priority TEXT DEFAULT 'Normal', -- meaning defined in enums.py file
    deadline TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    visible BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE task_assignments (
    id SERIAL PRIMARY KEY,
    task_id INTEGER REFERENCES tasks,
    user_id INTEGER REFERENCES users,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
