import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Header, Navbar, Nav } from "rsuite";
import CogIcon from '@rsuite/icons/legacy/Cog';

import "./navbar.scss";

function SideNavBar() {
  const [activeNav, setActiveNav] = useState("");
  const navigate = useNavigate();
  const onSelectNav = (eventKey: string) => {
    setActiveNav(eventKey);
    switch (eventKey) {
      case "home":
        navigate("/");
        break;
      case "explorer":
        navigate("/explorer");
        break;
      default:
        navigate("/");
    }
  };
  return (
    <>
      <div className="sidenav-container">
        <Header>
          <Navbar appearance="inverse">
            <Navbar.Brand>
              <a style={{ color: "#fff" }}>Ain - Logal AI</a>
            </Navbar.Brand>
            <Nav
              onSelect={onSelectNav}
              activeKey={activeNav}
              appearance="subtle"
            >
              <Nav.Item eventKey="explorer">Explorer</Nav.Item>
              <Nav.Item eventKey="home">Home</Nav.Item>
            </Nav>
            <Nav pullRight>
            <Nav.Item icon={<CogIcon />}>Settings</Nav.Item>
          </Nav>
          </Navbar>
        </Header>
      </div>
    </>
  );
}

export default SideNavBar;
