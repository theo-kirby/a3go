// C++ 3D-Go engine — same rules as the validated Python/TS engine: liberties,
// capture (priority over suicide), suicide rejection, positional superko (PSK),
// Tromp-Taylor area scoring. Standalone; modes selected by argv[1].
//   crossval        : read games from stdin, print TT breakdown per game
// (Phase B will add a selfplay mode.)
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>
#include <unordered_set>
#include <array>
#include <iostream>
#include <sstream>
#include <cmath>
#include <algorithm>

static const int EMPTY=0, BLACK=1, WHITE=2;
static inline int other(int c){ return c==BLACK?WHITE:BLACK; }

struct Board {
    int w,h,d;
    std::vector<int8_t> g;           // grid, index x*h*d + y*d + z
    int player;
    std::unordered_set<std::string> history;

    Board(int n): w(n),h(n),d(n), g(n*n*n, EMPTY), player(BLACK) {
        history.insert(hash());
    }
    inline int idx(int x,int y,int z) const { return (x*h + y)*d + z; }
    inline bool inb(int x,int y,int z) const { return x>=0&&x<w&&y>=0&&y<h&&z>=0&&z<d; }
    std::string hash() const { return std::string(reinterpret_cast<const char*>(g.data()), g.size()); }

    // neighbors offsets
    void neigh(int x,int y,int z, int out[][3], int& m) const {
        static const int D[6][3]={{1,0,0},{-1,0,0},{0,1,0},{0,-1,0},{0,0,1},{0,0,-1}};
        m=0;
        for(auto&o:D){int nx=x+o[0],ny=y+o[1],nz=z+o[2]; if(inb(nx,ny,nz)){out[m][0]=nx;out[m][1]=ny;out[m][2]=nz;m++;}}
    }
    // flood-fill group at (x,y,z); fills `stones` (indices) and returns liberty count
    int group(int x,int y,int z, std::vector<int>& stones) const {
        int color=g[idx(x,y,z)];
        stones.clear();
        std::vector<int> stack; stack.push_back(idx(x,y,z));
        std::vector<char> seen(g.size(),0); seen[idx(x,y,z)]=1;
        std::unordered_set<int> libs;
        while(!stack.empty()){
            int cur=stack.back(); stack.pop_back(); stones.push_back(cur);
            int cz=cur%d, cy=(cur/d)%h, cx=cur/(d*h);
            int nb[6][3],m; neigh(cx,cy,cz,nb,m);
            for(int i=0;i<m;i++){int ni=idx(nb[i][0],nb[i][1],nb[i][2]); int v=g[ni];
                if(v==EMPTY) libs.insert(ni);
                else if(v==color && !seen[ni]){seen[ni]=1; stack.push_back(ni);} }
        }
        return (int)libs.size();
    }
    // play (returns true if legal & applied). enforces capture/suicide/superko.
    bool play(int x,int y,int z){
        if(g[idx(x,y,z)]!=EMPTY) return false;
        std::vector<int8_t> snap=g;
        int color=player, opp=other(color);
        g[idx(x,y,z)]=color;
        int nb[6][3],m; neigh(x,y,z,nb,m);
        std::vector<int> grp;
        for(int i=0;i<m;i++){int nx=nb[i][0],ny=nb[i][1],nz=nb[i][2];
            if(g[idx(nx,ny,nz)]==opp){ if(group(nx,ny,nz,grp)==0){ for(int s:grp) g[s]=EMPTY; } } }
        if(group(x,y,z,grp)==0){ g=snap; return false; } // suicide
        std::string hh=hash();
        if(history.count(hh)){ g=snap; return false; } // superko
        history.insert(hh);
        player=opp;
        return true;
    }
    void pass_move(){ player=other(player); }

    // rollout-only move: capture + suicide, NO superko/history (matches Python play_fast)
    bool play_fast(int x,int y,int z){
        if(g[idx(x,y,z)]!=EMPTY) return false;
        std::vector<int8_t> snap=g;
        int color=player, opp=other(color);
        g[idx(x,y,z)]=color;
        int nb[6][3],m; neigh(x,y,z,nb,m);
        std::vector<int> grp;
        for(int i=0;i<m;i++){int nx=nb[i][0],ny=nb[i][1],nz=nb[i][2];
            if(g[idx(nx,ny,nz)]==opp){ if(group(nx,ny,nz,grp)==0){ for(int s:grp) g[s]=EMPTY; } } }
        if(group(x,y,z,grp)==0){ g=snap; return false; }
        player=opp; return true;
    }
    bool simple_eye(int x,int y,int z,int color) const {
        int nb[6][3],m; neigh(x,y,z,nb,m); if(m==0) return false;
        for(int i=0;i<m;i++) if(g[idx(nb[i][0],nb[i][1],nb[i][2])]!=color) return false;
        return true;
    }

    // Tromp-Taylor area scoring (komi 0). Fills outputs.
    void score(int& bs,int& ws,int& bt,int& wt,int& neu,int& diff,std::string& winner) const {
        bs=ws=bt=wt=neu=0;
        for(auto v:g){ if(v==BLACK)bs++; else if(v==WHITE)ws++; }
        std::vector<char> vis(g.size(),0);
        for(int x=0;x<w;x++)for(int y=0;y<h;y++)for(int z=0;z<d;z++){
            int id=idx(x,y,z);
            if(vis[id]||g[id]!=EMPTY) continue;
            std::vector<int> stack; stack.push_back(id); vis[id]=1;
            int region=0; bool bb=false,wb=false;
            while(!stack.empty()){int cur=stack.back();stack.pop_back();region++;
                int cz=cur%d,cy=(cur/d)%h,cx=cur/(d*h);
                int nb[6][3],m;neigh(cx,cy,cz,nb,m);
                for(int i=0;i<m;i++){int ni=idx(nb[i][0],nb[i][1],nb[i][2]);int v=g[ni];
                    if(v==EMPTY){if(!vis[ni]){vis[ni]=1;stack.push_back(ni);}}
                    else if(v==BLACK)bb=true; else if(v==WHITE)wb=true;} }
            if(bb&&!wb)bt+=region; else if(wb&&!bb)wt+=region; else neu+=region;
        }
        int ba=bs+bt, wa=ws+wt; diff=ba-wa;
        winner = diff>0?"black":(diff<0?"white":"draw");
    }
};

// ---- RNG (xorshift) ----
struct Rng{ uint64_t s; Rng(uint64_t seed):s(seed?seed:0x9e3779b97f4a7c15ULL){}
    uint64_t next(){ s^=s<<13; s^=s>>7; s^=s<<17; return s; }
    double uni(){ return (next()>>11)*(1.0/9007199254740992.0); }
    int rint(int n){ return (int)(next()%n); }
};

// ---- classical UCT MCTS over the C++ engine ----
struct Node{ Board b; int passes; int player; std::vector<int> untried; std::vector<Node*> ch;
    std::vector<int> moves; double N=0,Q=0; int move=-2; Node* parent=nullptr;
    Node(const Board& bb,int p):b(bb),passes(p),player(bb.player){} };

static void legal_play_moves(const Board& b, std::vector<int>& out){
    out.clear(); int n=b.w;
    for(int x=0;x<n;x++)for(int y=0;y<n;y++)for(int z=0;z<n;z++){
        if(b.g[b.idx(x,y,z)]!=EMPTY) continue;
        Board t=b; if(t.play(x,y,z)) out.push_back(x*n*n+y*n+z);
    }
    out.push_back(n*n*n); // pass
}

// fast random playout to terminal; returns winner: 1 black, 2 white, 0 draw
static int rollout(Board b,int passes,Rng& rng,int cap){
    int n=b.w; std::vector<int> empt;
    for(int step=0; step<cap; step++){
        if(passes>=2) break;
        empt.clear();
        for(int i=0;i<(int)b.g.size();i++) if(b.g[i]==EMPTY) empt.push_back(i);
        // shuffle
        for(int i=(int)empt.size()-1;i>0;i--){int j=rng.rint(i+1); std::swap(empt[i],empt[j]);}
        bool played=false; int color=b.player;
        for(int id:empt){ int z=id%n, y=(id/n)%n, x=id/(n*n);
            if(b.simple_eye(x,y,z,color)) continue;
            if(b.play_fast(x,y,z)){ played=true; passes=0; break; } }
        if(!played){ b.pass_move(); passes++; }
    }
    int bs,ws,bt,wt,neu,diff; std::string win; b.score(bs,ws,bt,wt,neu,diff,win);
    return win=="black"?1:(win=="white"?2:0);
}

static void free_tree(Node* nd){ for(auto c:nd->ch) free_tree(c); delete nd; }

// run MCTS from (board,passes); fill visit counts over n^3+1 actions
static void mcts(const Board& board,int passes,int playouts,double cpuct,Rng& rng,int cap,std::vector<double>& visits){
    int n=board.w, A=n*n*n+1;
    Node* root=new Node(board,passes);
    legal_play_moves(root->b, root->untried);
    int root_player=board.player;
    for(int it=0; it<playouts; it++){
        Node* nd=root;
        // selection
        while(nd->untried.empty() && !nd->ch.empty()){
            double logN=std::log(nd->N+1), best=-1e18; Node* bc=nullptr;
            for(auto c:nd->ch){ double v=c->Q/std::max(c->N,1.0)+cpuct*std::sqrt(logN/std::max(c->N,1.0));
                if(v>best){best=v;bc=c;} }
            nd=bc;
        }
        // expansion
        if(!nd->untried.empty()){
            int ui=rng.rint((int)nd->untried.size()); int a=nd->untried[ui];
            nd->untried.erase(nd->untried.begin()+ui);
            Board nb=nd->b; int np=nd->passes;
            if(a==n*n*n){ nb.pass_move(); np=nd->passes+1; } else { nb.play(a/(n*n), (a/n)%n, a%n); np=0; }
            Node* c=new Node(nb,np); c->move=a; c->parent=nd; legal_play_moves(c->b,c->untried);
            nd->ch.push_back(c); nd=c;
        }
        // simulation
        int win = (nd->passes>=2) ? ({int bs,ws,bt,wt,neu,diff;std::string w;nd->b.score(bs,ws,bt,wt,neu,diff,w); (w=="black"?1:(w=="white"?2:0));})
                                  : rollout(nd->b, nd->passes, rng, cap);
        double reward = (win==0)?0.5 : (((win==1)==(root_player==BLACK))?1.0:0.0);
        // backprop
        for(Node* p=nd; p; p=p->parent){ p->N+=1; p->Q+=reward; }
    }
    visits.assign(A,0.0);
    for(auto c:root->ch) visits[c->move]=c->N;
    free_tree(root);
}

// self-play one game, append (planes, policy, z) to buffers
static void selfplay_game(int n,int playouts,int cap,int temp_moves,Rng& rng,
                          std::vector<float>& X,std::vector<float>& P,std::vector<float>& Z){
    int A=n*n*n+1; Board b(n); int passes=0;
    std::vector<std::vector<float>> planes; std::vector<std::vector<float>> pols; std::vector<int> players;
    int maxmoves=n*n*n*2;
    for(int t=0;t<maxmoves;t++){
        if(passes>=2) break;
        std::vector<double> vis; mcts(b,passes,playouts,1.4,rng,cap,vis);
        double sum=0; for(double v:vis) sum+=v;
        std::vector<float> pi(A,0.f);
        if(sum>0) for(int a=0;a<A;a++) pi[a]=(float)(vis[a]/sum);
        else pi[n*n*n]=1.f;
        // encode planes
        std::vector<float> pl(3*n*n*n,0.f);
        for(int i=0;i<n*n*n;i++){ pl[i]=(b.g[i]==BLACK)?1.f:0.f; pl[n*n*n+i]=(b.g[i]==WHITE)?1.f:0.f; pl[2*n*n*n+i]=(b.player==BLACK)?1.f:0.f; }
        planes.push_back(pl); pols.push_back(pi); players.push_back(b.player);
        // choose move: temp~1 sample first temp_moves, else argmax
        int a;
        if(t<temp_moves && sum>0){ double r=rng.uni()*sum, acc=0; a=n*n*n; for(int k=0;k<A;k++){acc+=vis[k]; if(r<=acc){a=k;break;}} }
        else { int best=0; double bv=-1; for(int k=0;k<A;k++) if(vis[k]>bv){bv=vis[k];best=k;} a=best; }
        if(a==n*n*n){ b.pass_move(); passes++; } else { b.play(a/(n*n),(a/n)%n,a%n); passes=0; }
    }
    int bs,ws,bt,wt,neu,diff; std::string win; b.score(bs,ws,bt,wt,neu,diff,win);
    int winner = win=="black"?1:(win=="white"?2:0);
    for(size_t i=0;i<planes.size();i++){
        float z = (winner==0)?0.f : ((winner==players[i])?1.f:-1.f);
        for(float v:planes[i]) X.push_back(v);
        for(float v:pols[i]) P.push_back(v);
        Z.push_back(z);
    }
}

int main(int argc,char**argv){
    std::string mode = argc>1?argv[1]:"crossval";
    if(mode=="selfplay"){
        // selfplay n games playouts cap seed outfile
        int n=std::stoi(argv[2]), games=std::stoi(argv[3]), playouts=std::stoi(argv[4]);
        int cap=std::stoi(argv[5]); uint64_t seed=std::stoull(argv[6]); std::string outf=argv[7];
        Rng rng(seed);
        std::vector<float> X,P,Z;
        for(int gI=0; gI<games; gI++) selfplay_game(n,playouts,cap,8,rng,X,P,Z);
        int32_t count=(int32_t)Z.size(), nn=n;
        FILE* f=fopen(outf.c_str(),"wb");
        fwrite(&count,4,1,f); fwrite(&nn,4,1,f);
        fwrite(X.data(),4,X.size(),f); fwrite(P.data(),4,P.size(),f); fwrite(Z.data(),4,Z.size(),f);
        fclose(f);
        fprintf(stderr,"selfplay n=%d games=%d playouts=%d -> %d examples\n",n,games,playouts,count);
        return 0;
    }
    if(mode=="crossval"){
        int G; if(!(std::cin>>G)) return 1;
        for(int gi=0; gi<G; gi++){
            int n,k; std::cin>>n>>k;
            Board b(n);
            for(int j=0;j<k;j++){
                std::string tok; std::cin>>tok;
                if(tok=="p"){ b.pass_move(); }
                else{ int x,y,z; char c; std::stringstream ss(tok); ss>>x>>c>>y>>c>>z;
                    if(!b.play(x,y,z)){ fprintf(stderr,"ILLEGAL game %d move %d %s\n",gi,j,tok.c_str()); } }
            }
            int bs,ws,bt,wt,neu,diff; std::string win;
            b.score(bs,ws,bt,wt,neu,diff,win);
            printf("%d %d %d %d %d %d %s\n",bs,ws,bt,wt,neu,diff,win.c_str());
        }
    }
    return 0;
}
