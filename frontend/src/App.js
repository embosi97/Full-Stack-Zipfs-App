import logo from './logo.svg';
import './App.css';
import { Button, Nav, Navbar, Container, NavDropdown } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import { render } from 'react-dom';
import React from 'react'

class App extends React.Component {
    constructor(props){
        super(props);

        this.state = {
            name: 'J',
            apppVersion: '1'
        }
    }
    render(){
        return(
          <Navbar bg="light" expand="lg">
            <Navbar.Brand href="../build/HomePage.html"> IsItZipf's? </Navbar.Brand>
            <Navbar.Toggle aria-controls="basic-navbar-nav" />
            <Navbar.Collapse className="justify-content-end">
              <Nav>
                <Nav.Link href="#link">Get Started</Nav.Link>
                <NavDropdown title="Dropdown" id="basic-nav-dropdown">
                  <NavDropdown.Item href="https://github.com/embosi97">GitHub</NavDropdown.Item>
                  <NavDropdown.Divider />
                  <NavDropdown.Item href="https://www.linkedin.com/in/emiljano-bodaj-ny97/">LinkedIn</NavDropdown.Item>
                  <NavDropdown.Divider />
                  <NavDropdown.Item href="http://embosi97.pythonanywhere.com/">Portfolio</NavDropdown.Item>
                </NavDropdown>
                <Nav.Link href="https://en.wikipedia.org/wiki/Zipf%27s_law">More Info</Nav.Link>
              </Nav>
            </Navbar.Collapse>
        </Navbar>
        )
    }
}
export default App;
