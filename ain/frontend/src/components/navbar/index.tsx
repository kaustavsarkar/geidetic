import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Sidenav, Nav } from "rsuite";

import './navbar.scss';

interface IProps {
  expanded: boolean;
}

function SideNavBar(props: IProps) {
  const [expanded, setExpanded] = useState(props.expanded);
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
        <Sidenav expanded={expanded}>
          <Sidenav.Header>
            <div className="header">Ain - Legal AI</div>
          </Sidenav.Header>
          <Sidenav.Body>
            <Nav
              onSelect={onSelectNav}
              activeKey={activeNav}
              appearance="subtle"
            >
              <Nav.Item eventKey="explorer">Explorer</Nav.Item>
              <Nav.Item eventKey="home">Home</Nav.Item>
            </Nav>
          </Sidenav.Body>
          <Sidenav.Toggle onToggle={setExpanded} />
        </Sidenav>
      </div>
    </>
  );
}

export default SideNavBar;
