export function HeroSection() {
  return (
    <section className="bg-gradient-to-br from-secondary/20 via-secondary/10 to-background border-b border-border">
      <div className="container mx-auto px-6 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center max-w-7xl mx-auto">
          <div className="space-y-6">
            <div className="inline-block px-4 py-2 bg-secondary/30 rounded-full border border-secondary/40">
              <span className="text-sm text-secondary-foreground">16th - 19th Century European Collections</span>
            </div>
            <h2 className="text-4xl lg:text-5xl text-foreground leading-tight">
              Explore Historic Alba Amicorum
            </h2>
            <p className="text-lg text-muted-foreground leading-relaxed">
              Discover a curated collection of friendship albums from Renaissance and Enlightenment Europe. 
              These remarkable manuscripts offer intimate glimpses into the social networks, artistic tastes, 
              and intellectual exchanges of their time.
            </p>
            <div className="flex gap-4 pt-4">
              <div className="text-center">
                <div className="text-3xl text-secondary">250+</div>
                <div className="text-sm text-muted-foreground">Albums</div>
              </div>
              <div className="w-px bg-border"></div>
              <div className="text-center">
                <div className="text-3xl text-secondary">15</div>
                <div className="text-sm text-muted-foreground">Countries</div>
              </div>
              <div className="w-px bg-border"></div>
              <div className="text-center">
                <div className="text-3xl text-secondary">400</div>
                <div className="text-sm text-muted-foreground">Years</div>
              </div>
            </div>
          </div>
          <div className="relative">
            <div className="absolute inset-0 bg-gradient-to-br from-secondary/30 to-transparent rounded-2xl blur-2xl"></div>
            <img 
              src="https://images.unsplash.com/photo-1603361233308-b3ec0f7c0a16?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxhbnRpcXVlJTIwYWxidW0lMjAxNnRoJTIwY2VudHVyeSUyMG1hbnVzY3JpcHR8ZW58MXx8fHwxNzc2NTkzMzAzfDA&ixlib=rb-4.1.0&q=80&w=1080&utm_source=figma&utm_medium=referral"
              alt="Historic Alba Amicorum"
              className="relative rounded-2xl shadow-2xl w-full object-cover aspect-[4/3] border border-border/50"
            />
          </div>
        </div>
      </div>
    </section>
  );
}
