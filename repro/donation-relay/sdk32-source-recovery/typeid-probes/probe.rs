pub fn boxed(s: String) -> Box<dyn std::error::Error + Send + Sync> { s.into() }
