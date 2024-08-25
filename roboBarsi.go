package main

import (
    "database/sql"
    "fmt"
    "log"

    _ "github.com/go-sql-driver/mysql"
)

func main() {
    // Conectar ao banco de dados
    db, err := sql.Open("mysql", "usuario:senha@tcp(127.0.0.1:3306)/nome_do_banco")
    if err != nil {
        log.Fatal(err)
    }
    defer db.Close()

    // Verificar a conexão
    err = db.Ping()
    if err != nil {
        log.Fatal(err)
    }
    fmt.Println("Conexão bem-sucedida!")

    // Criar uma tabela
    _, err = db.Exec(`CREATE TABLE IF NOT EXISTS usuarios (
        id INT AUTO_INCREMENT,
        nome VARCHAR(50),
        idade INT,
     		package main
		
		import (
			"database/sql"
			"fmt"
			"log"
		
			_ "github.com/go-sql-driver/mysql"
		)
		
		func main() {
			// Conectar ao banco de dados
			db, err := sql.Open("mysql", "usuario:senha@tcp(127.0.0.1:3306)/nome_do_banco")
			if err != nil {
				log.Fatal(err)
			}
			defer db.Close()
		
			// Verificar a conexão
			err = db.Ping()
			if err != nil {
				log.Fatal(err)
			}
			fmt.Println("Conexão bem-sucedida!")
		
			// Criar uma tabela
			_, err = db.Exec(`CREATE TABLE IF NOT EXISTS usuarios (
				id INT AUTO_INCREMENT,
				nome VARCHAR(50),
				idade INT,
				PRIMARY KEY (id)
			)`)
			if err != nil {
				log.Fatal(err)
			}
			fmt.Println("Tabela criada com sucesso!")
		
			// Inserir dados
			_, err = db.Exec(`INSERT INTO usuarios (nome, idade) VALUES (?, ?)`, "João", 30)
			if err != nil {
				log.Fatal(err)
			}
			fmt.Println("Dados inseridos com sucesso!")
		}   PRIMARY KEY (id)
    )`)
    if err != nil {
        log.Fatal(err)
    }
    fmt.Println("Tabela criada com sucesso!")

    // Inserir dados
    _, err = db.Exec(`INSERT INTO usuarios (nome, idade) VALUES (?, ?)`, "João", 30)
    if err != nil {
        log.Fatal(err)
    }
    fmt.Println("Dados inseridos com sucesso!")

    // Consultar dados
    rows, err := db.Query(`SELECT id, nome, idade FROM usuarios`)
    if err != nil {
        log.Fatal(err)
    }
    defer rows.Close()

    fmt.Println("Dados da tabela usuarios:")
    for rows.Next() {
        var id int
        var nome string
        var idade int
        err := rows.Scan(&id, &nome, &idade)
        if err != nil {
            log.Fatal(err)
        }
        fmt.Printf("ID: %d, Nome: %s, Idade: %d\n", id, nome, idade)
    }

    // Verificar erros na iteração
    err = rows.Err()
    if err != nil {
        log.Fatal(err)
    }
}