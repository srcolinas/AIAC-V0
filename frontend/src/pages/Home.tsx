import { Link } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import './Home.css'

export default function Home() {
  const { isAuthenticated } = useAuthStore()
  
  return (
    <div className="home">
      {/* Hero Section */}
      <section className="hero">
        <div className="hero-background">
          <div className="mountain mountain-1" />
          <div className="mountain mountain-2" />
          <div className="mountain mountain-3" />
          <div className="sun" />
        </div>
        
        <div className="hero-content animate-slide-up">
          <div className="hero-badge">Strategy Board Game</div>
          <h1 className="hero-title">Teyuna</h1>
          <p className="hero-subtitle">The Lost City</p>
          <p className="hero-description">
            Build your community in the shadow of the sacred mountains. 
            Gather resources, construct bohíos and temples, and honor the 
            ancient traditions of the Tayrona people.
          </p>
          
          <div className="hero-actions">
            {isAuthenticated ? (
              <Link to="/lobby" className="btn btn-primary btn-lg">
                Enter the City
              </Link>
            ) : (
              <>
                <Link to="/register" className="btn btn-primary btn-lg">
                  Begin Your Journey
                </Link>
                <Link to="/login" className="btn btn-secondary btn-lg">
                  Return to Teyuna
                </Link>
              </>
            )}
          </div>
        </div>
      </section>
      
      {/* Features Section */}
      <section className="features">
        <h2 className="section-title border-tayrona">The Way of Teyuna</h2>
        
        <div className="features-grid">
          <div className="feature-card animate-fade-in" style={{ animationDelay: '0.1s' }}>
            <div className="feature-icon">
              <svg viewBox="0 0 48 48" fill="none">
                <circle cx="24" cy="24" r="20" stroke="currentColor" strokeWidth="2" />
                <circle cx="24" cy="24" r="8" fill="currentColor" opacity="0.3" />
                <path d="M24 4v8M24 36v8M4 24h8M36 24h8" stroke="currentColor" strokeWidth="2" />
              </svg>
            </div>
            <h3>Oro (Gold)</h3>
            <p>Extract precious gold from the Sierra mountains, essential for building sacred temples.</p>
          </div>
          
          <div className="feature-card animate-fade-in" style={{ animationDelay: '0.2s' }}>
            <div className="feature-icon stone">
              <svg viewBox="0 0 48 48" fill="none">
                <polygon points="24,4 44,18 44,38 24,44 4,38 4,18" stroke="currentColor" strokeWidth="2" fill="currentColor" fillOpacity="0.2" />
                <polygon points="24,14 34,22 34,34 24,38 14,34 14,22" fill="currentColor" opacity="0.3" />
              </svg>
            </div>
            <h3>Piedra (Stone)</h3>
            <p>Quarry stone blocks to build the legendary terraces and paths of your settlement.</p>
          </div>
          
          <div className="feature-card animate-fade-in" style={{ animationDelay: '0.3s' }}>
            <div className="feature-icon cotton">
              <svg viewBox="0 0 48 48" fill="none">
                <circle cx="24" cy="20" r="8" stroke="currentColor" strokeWidth="2" />
                <circle cx="16" cy="28" r="6" stroke="currentColor" strokeWidth="2" />
                <circle cx="32" cy="28" r="6" stroke="currentColor" strokeWidth="2" />
                <path d="M24 32v12" stroke="currentColor" strokeWidth="2" />
              </svg>
            </div>
            <h3>Algodón (Cotton)</h3>
            <p>Harvest cotton from the highlands to weave textiles and trade with neighbors.</p>
          </div>
          
          <div className="feature-card animate-fade-in" style={{ animationDelay: '0.4s' }}>
            <div className="feature-icon maize">
              <svg viewBox="0 0 48 48" fill="none">
                <ellipse cx="24" cy="28" rx="8" ry="14" stroke="currentColor" strokeWidth="2" fill="currentColor" fillOpacity="0.2" />
                <path d="M24 14c-6 2-8 6-8 8M24 14c6 2 8 6 8 8" stroke="currentColor" strokeWidth="2" />
                <path d="M24 4v10" stroke="currentColor" strokeWidth="2" />
              </svg>
            </div>
            <h3>Maíz (Maize)</h3>
            <p>Cultivate maize in the fertile valleys to sustain your growing community.</p>
          </div>
          
          <div className="feature-card animate-fade-in" style={{ animationDelay: '0.5s' }}>
            <div className="feature-icon wood">
              <svg viewBox="0 0 48 48" fill="none">
                <path d="M24 4L36 20H12L24 4Z" stroke="currentColor" strokeWidth="2" fill="currentColor" fillOpacity="0.2" />
                <path d="M24 14L38 32H10L24 14Z" stroke="currentColor" strokeWidth="2" fill="currentColor" fillOpacity="0.3" />
                <rect x="20" y="32" width="8" height="12" fill="currentColor" opacity="0.4" />
              </svg>
            </div>
            <h3>Madera (Wood)</h3>
            <p>Gather wood from the jungle to build bohíos and construct stone paths.</p>
          </div>
          
          <div className="feature-card animate-fade-in" style={{ animationDelay: '0.6s' }}>
            <div className="feature-icon temple">
              <svg viewBox="0 0 48 48" fill="none">
                <path d="M8 40h32M12 40V28h24v12M16 28V20h16v8M20 20V14h8v6" stroke="currentColor" strokeWidth="2" />
                <circle cx="24" cy="10" r="4" fill="currentColor" opacity="0.3" />
              </svg>
            </div>
            <h3>Templos</h3>
            <p>Construct sacred temples to honor the ancestors and lead your people to victory.</p>
          </div>
        </div>
      </section>
      
      {/* How to Play */}
      <section className="how-to-play">
        <h2 className="section-title border-tayrona">Path to Victory</h2>
        
        <div className="steps">
          <div className="step">
            <div className="step-number">I</div>
            <div className="step-content">
              <h3>Gather Resources</h3>
              <p>Roll the dice and collect resources based on where your bohíos are placed on the board.</p>
            </div>
          </div>
          
          <div className="step">
            <div className="step-number">II</div>
            <div className="step-content">
              <h3>Build & Expand</h3>
              <p>Construct stone paths, bohíos, and temples to grow your settlement across the mountains.</p>
            </div>
          </div>
          
          <div className="step">
            <div className="step-number">III</div>
            <div className="step-content">
              <h3>Trade & Prosper</h3>
              <p>Trade resources with other players or at ports to obtain what you need.</p>
            </div>
          </div>
          
          <div className="step">
            <div className="step-number">IV</div>
            <div className="step-content">
              <h3>Achieve Glory</h3>
              <p>Be the first to reach 10 victory points by building, developing, and earning achievements.</p>
            </div>
          </div>
        </div>
      </section>
      
      {/* Call to Action */}
      <section className="cta">
        <div className="cta-content">
          <h2>Ready to Build Your Legacy?</h2>
          <p>Join players from around the world in this tribute to the ancient Tayrona civilization.</p>
          
          {isAuthenticated ? (
            <Link to="/lobby" className="btn btn-primary btn-lg">
              Start Playing
            </Link>
          ) : (
            <Link to="/register" className="btn btn-primary btn-lg">
              Create Account
            </Link>
          )}
        </div>
      </section>
    </div>
  )
}

